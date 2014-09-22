/*
 * kano_updater.c
 *
 * Copyright (C) 2014 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
 *
 */

#include <gtk/gtk.h>
#include <gdk/gdk.h>
#include <glib/gi18n.h>
#include <gdk-pixbuf/gdk-pixbuf.h>
#include <gio/gio.h>

#include <lxpanel/plugin.h>

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <time.h>

#include <kdesk-hourglass.h>

#define DEFAULT_ICON_FILE "/usr/share/kano-updater/images/panel-default.png"
#define NOTIFICATION_ICON_FILE "/usr/share/kano-updater/images/panel-notification.png"
#define UPDATE_STATUS_FILE "/var/cache/kano-updater/status"

#define CHECK_FOR_UPDATES_CMD "sudo check-for-updates"
#define UPDATE_CMD "kdesk-blur 'sudo kano-updater'"

#define PLUGIN_TOOLTIP "Kano Updater"

#define DAY 60*60*24

Panel *panel;

typedef struct {
	int last_update;
	int last_check;
	int update_available;

	GtkWidget *icon;

	guint timer;
} kano_updater_plugin_t;

static gboolean show_menu(GtkWidget *, GdkEventButton *,
			  kano_updater_plugin_t *);
static void selection_done(GtkWidget *);
static void popup_set_position(GtkWidget *, gint *, gint *, gboolean *,
			       GtkWidget *);
static gboolean update_status(kano_updater_plugin_t *);

static int plugin_constructor(Plugin *p, char **fp)
{
	(void)fp;

	panel = p->panel;

	/* allocate our private structure instance */
	kano_updater_plugin_t *plugin = g_new0(kano_updater_plugin_t, 1);

	plugin->last_update = 0;
	plugin->last_check = 0;
	plugin->update_available = 0;

	/* put it where it belongs */
	p->priv = plugin;

	GtkWidget *icon = gtk_image_new_from_file(DEFAULT_ICON_FILE);
	plugin->icon = icon;

	/* need to create a widget to show */
	p->pwid = gtk_event_box_new();

	/* set border width */
	gtk_container_set_border_width(GTK_CONTAINER(p->pwid), 0);

	/* add the label to the container */
	gtk_container_add(GTK_CONTAINER(p->pwid), GTK_WIDGET(icon));

	/* our widget doesn't have a window... */
	gtk_widget_set_has_window(p->pwid, FALSE);


	gtk_signal_connect(GTK_OBJECT(p->pwid), "button-press-event",
			   GTK_SIGNAL_FUNC(show_menu), plugin);


	/* Set a tooltip to the icon to show when the mouse sits over the it */
	GtkTooltips *tooltips;
	tooltips = gtk_tooltips_new();
	gtk_tooltips_set_tip(tooltips, GTK_WIDGET(icon), PLUGIN_TOOLTIP, NULL);

	gtk_widget_set_sensitive(icon, TRUE);

	plugin->timer = g_timeout_add(60000, (GSourceFunc) update_status,
				      (gpointer) plugin);

	update_status(plugin);

	/* show our widget */
	gtk_widget_show_all(p->pwid);

	return 1;
}

static void plugin_destructor(Plugin *p)
{
	kano_updater_plugin_t *plugin = (kano_updater_plugin_t *)p->priv;

	/* Disconnect the timer. */
	g_source_remove(plugin->timer);

	g_free(plugin);
}

static int parse_line(char *line, const char const *key, int *value)
{
	if (strncmp(line, key, strlen(key)) == 0) {
		*value = atoi(line + strlen(key));
		return 0;
	}

	return -1;
}

static void launch_cmd(const char *cmd)
{
	GAppInfo *appinfo = NULL;
	gboolean ret = FALSE;

	appinfo = g_app_info_create_from_commandline(cmd, NULL,
				G_APP_INFO_CREATE_NONE, NULL);

	if (appinfo == NULL) {
		perror("Command lanuch failed.");
		return;
	}

	ret = g_app_info_launch(appinfo, NULL, NULL, NULL);
	if (!ret)
		perror("Command lanuch failed.");
}

static gboolean check_for_updates(kano_updater_plugin_t *plugin)
{
	launch_cmd(CHECK_FOR_UPDATES_CMD);
	return TRUE;
}

static gboolean update_status(kano_updater_plugin_t *plugin)
{
	FILE *fp;
	char *line = NULL;
	size_t len = 0;
	ssize_t read;
	int value = 0;

	int now = time(NULL);

	fp = fopen(UPDATE_STATUS_FILE, "r");
	if (fp == NULL)
		/* In case the status file isn't there, we say there
		   are no updates available. */
		return TRUE;

	while ((read = getline(&line, &len, fp)) != -1) {
		if (parse_line(line, "last_update=", &value) == 0)
			plugin->last_update = value;
		else if (parse_line(line, "last_check=", &value) == 0)
			plugin->last_check = value;
		else if (parse_line(line, "update_available=", &value) == 0)
			plugin->update_available = value;
	}

	if (line)
		free(line);

	fclose(fp);

	/* printf("lu%d lc%d ua%d\n", plugin->last_update,
				   plugin->last_check,
				   plugin->update_available); */

	if (plugin->update_available > 0) {
		/* Change the icon to red */
		gtk_image_set_from_file(GTK_IMAGE(plugin->icon),
						  NOTIFICATION_ICON_FILE);
	} else {
		/* Change the icon to white */
		gtk_image_set_from_file(GTK_IMAGE(plugin->icon),
					DEFAULT_ICON_FILE);

		if ((now - plugin->last_check) >= DAY) {
			printf("running update check/n");
			check_for_updates(plugin);
		}
	}

	return TRUE;
}

void update_clicked(GtkWidget *widget, gpointer data)
{
        kdesk_hourglass_start("kano-updater");
	launch_cmd(UPDATE_CMD);
}

void check_for_update_clicked(GtkWidget *widget, kano_updater_plugin_t *plugin)
{
	check_for_updates(plugin);
}

static gboolean show_menu(GtkWidget *widget, GdkEventButton *event,
		      kano_updater_plugin_t *plugin)
{
	GtkWidget *menu = gtk_menu_new();
	GtkWidget *header_item, *update_item, *check_item,
		  *no_updates_item;

	if (event->button != 1)
		return FALSE;

	update_status(plugin);

	/* Create the menu items */
	header_item = gtk_menu_item_new_with_label("Kano Updater");
	gtk_widget_set_sensitive(header_item, FALSE);
	gtk_menu_append(GTK_MENU(menu), header_item);
	gtk_widget_show(header_item);

	if (plugin->update_available > 0) {
		update_item = gtk_menu_item_new_with_label("Update your system");
		g_signal_connect(update_item, "activate",
				 G_CALLBACK(update_clicked), NULL);
		gtk_menu_append(GTK_MENU(menu), update_item);
		gtk_widget_show(update_item);
	} else {
		no_updates_item = gtk_menu_item_new_with_label("No updates found");
		gtk_widget_set_sensitive(no_updates_item, FALSE);
		gtk_menu_append(GTK_MENU(menu), no_updates_item);
		gtk_widget_show(no_updates_item);

		check_item = gtk_menu_item_new_with_label("Check again");
		g_signal_connect(check_item, "activate",
				 G_CALLBACK(check_for_update_clicked),
				 plugin);
		gtk_menu_append(GTK_MENU(menu), check_item);
		gtk_widget_show(check_item);
	}

	g_signal_connect(menu, "selection-done",
			 G_CALLBACK(selection_done), NULL);

	/* Show the menu. */
	gtk_menu_popup(GTK_MENU(menu), NULL, NULL,
		       (GtkMenuPositionFunc) popup_set_position, widget,
		       event->button, event->time);

	return TRUE;
}

static void selection_done(GtkWidget *menu)
{
    gtk_widget_destroy(menu);
}

/* Helper for position-calculation callback for popup menus. */
void lxpanel_plugin_popup_set_position_helper(Panel * p, GtkWidget * near,
	GtkWidget * popup, GtkRequisition * popup_req, gint * px, gint * py)
{
	/* Get the origin of the requested-near widget in
	   screen coordinates. */
	gint x, y;
	gdk_window_get_origin(GDK_WINDOW(near->window), &x, &y);

	/* Doesn't seem to be working according to spec; the allocation.x
	   sometimes has the window origin in it */
	if (x != near->allocation.x) x += near->allocation.x;
	if (y != near->allocation.y) y += near->allocation.y;

	/* Dispatch on edge to lay out the popup menu with respect to
	   the button. Also set "push-in" to avoid any case where it
	   might flow off screen. */
	switch (p->edge)
	{
		case EDGE_TOP:    y += near->allocation.height; break;
		case EDGE_BOTTOM: y -= popup_req->height;       break;
		case EDGE_LEFT:   x += near->allocation.width;  break;
		case EDGE_RIGHT:  x -= popup_req->width;        break;
	}
	*px = x;
	*py = y;
}

/* Position-calculation callback for popup menu. */
static void popup_set_position(GtkWidget *menu, gint *px, gint *py,
				gboolean *push_in, GtkWidget *p)
{
    /* Get the allocation of the popup menu. */
    GtkRequisition popup_req;
    gtk_widget_size_request(menu, &popup_req);

    /* Determine the coordinates. */
    lxpanel_plugin_popup_set_position_helper(panel, p, menu, &popup_req, px, py);
    *push_in = TRUE;
}

static void plugin_configure(Plugin *p, GtkWindow *parent)
{
  // doing nothing here, so make sure neither of the parameters
  // emits a warning at compilation
  (void)p;
  (void)parent;
}

static void plugin_save_configuration(Plugin *p, FILE *fp)
{
  // doing nothing here, so make sure neither of the parameters
  // emits a warning at compilation
  (void)p;
  (void)fp;
}

/* Plugin descriptor. */
PluginClass kano_updater_plugin_class = {
	// this is a #define taking care of the size/version variables
	PLUGINCLASS_VERSIONING,

	// type of this plugin
	type : "kano_updater",
	name : N_("Kano Updater"),
	version: "1.0.2",
	description : N_("Keep your Kano OS up-to-date."),

	// we can have many running at the same time
	one_per_system : FALSE,

	// can't expand this plugin
	expand_available : FALSE,

	// assigning our functions to provided pointers.
	constructor : plugin_constructor,
	destructor  : plugin_destructor,
	config : plugin_configure,
	save : plugin_save_configuration
};
