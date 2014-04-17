/*
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

#define ICON_FILE "/usr/share/kano-desktop/images/updater.png"
#define UPDATE_STATUS_FILE "/var/cache/kano-updater/status"

#define WEEK 60*60*24*7

static int instance_cnt = 0;
Panel *panel;

typedef struct {
	gint my_id;
	guint timer;
} kano_updater_plugin_t;

static gint show_menu(GtkWidget *, GdkEventButton *);
static void selection_done(GtkWidget *);
static void popup_set_position(GtkWidget *, gint *, gint *, gboolean *,
			       GtkWidget *);
static gboolean check_for_update(kano_updater_plugin_t *);

static int plugin_constructor(Plugin *p, char **fp)
{
	(void)fp;

	panel = p->panel;

	/* allocate our private structure instance */
	kano_updater_plugin_t *plugin = g_new0(kano_updater_plugin_t, 1);

	/* put it where it belongs */
	p->priv = plugin;

	/* update the instance count */
	plugin->my_id = ++instance_cnt;

	/* make a label out of the ID */
	char id_buf[10] = {'\0'};
	sprintf(id_buf, "TP-%d", plugin->my_id);

	GtkWidget *icon = gtk_image_new_from_file(ICON_FILE);

	/* need to create a widget to show */
	p->pwid = gtk_event_box_new();

	/* set border width */
	gtk_container_set_border_width(GTK_CONTAINER(p->pwid), 0);

	/* add the label to the container */
	gtk_container_add(GTK_CONTAINER(p->pwid), GTK_WIDGET(icon));

	/* our widget doesn't have a window... */
	gtk_widget_set_has_window(p->pwid, FALSE);


	gtk_signal_connect(GTK_OBJECT(p->pwid), "button_press_event",
			   GTK_SIGNAL_FUNC(show_menu), NULL);

	//gtk_widget_set_state(icon, GTK_STATE_SELECTED); // GTK_STATE_NORMAL
	gtk_widget_set_sensitive(icon, TRUE);

	plugin->timer = g_timeout_add(3000/*00TODO*/, (GSourceFunc) check_for_update,
				      (gpointer) p);

	/* show our widget */
	gtk_widget_show_all(p->pwid);

	return 1;
}

static int parse_line(char *line, const char const *key, int *value)
{
	if (strncmp(line, key, strlen(key)) == 0) {
		*value = atoi(line + strlen(key));
		return 0;
	}

	return -1;
}

static gboolean check_for_update(kano_updater_plugin_t *plugin)
{
	//printf("Checking for update\n");
	FILE *fp;
	char *line = NULL;
	size_t len = 0;
	ssize_t read;
	int last_check = 0, last_update = 0, update_available = 0, value = 0;

	fp = fopen(UPDATE_STATUS_FILE, "r");
	if (fp == NULL)
		/* In case the status file isn't there, we say there
		   are no updates available. */
		return TRUE;

	while ((read = getline(&line, &len, fp)) != -1) {
		if (parse_line(line, "last_update=", &value) == 0)
			last_update = value;
		else if (parse_line(line, "last_check=", &value) == 0)
			last_check = value;
		else if (parse_line(line, "update_available=", &value) == 0)
			update_available = value;
	}

	if (line)
		free(line);

	fclose(fp);

	printf("lu%d lc%d ua%d\n", last_update, last_check, update_available);

	if (update_available > 0) {
		/* Change the icon to red, enable the label */
	} else {
		int now = time(NULL);
		if ((now - last_check) >= WEEK) {
			/* fork() && exec() */
			/* start wait polling */
			/* block update checks until the process terminates */
		} else {
			/* Set icon to white, disable label */
		}
	}

	return TRUE;
}

static gint show_menu(GtkWidget *widget, GdkEventButton *event)
{
	printf("abc\n");


	//G_APP_INFO_CREATE_NONE
	//G_APP_INFO_CREATE_NEEDS_TERMINAL
	GAppInfo *appinfo = NULL;
	gboolean ret = FALSE;

	appinfo = g_app_info_create_from_commandline("sudo kano-updater",
			NULL, G_APP_INFO_CREATE_NONE, NULL);

	//g_assert(appinfo != NULL); // TODO error handling is not implemented.
	ret = g_app_info_launch(appinfo, NULL, NULL, NULL);
	//g_assert(ret == TRUE); // TODO error handling is not implemented.



	GtkWidget *menu = gtk_menu_new();
	GtkWidget *header_item, *update_item;

	/* Create the menu items */
	header_item = gtk_menu_item_new_with_label("Kano OS Updates");
	gtk_widget_set_sensitive(header_item, FALSE);
	update_item = gtk_menu_item_new_with_label("Update your system");

	/* Add them to the menu */
	gtk_menu_append(GTK_MENU(menu), header_item);
	gtk_menu_append(GTK_MENU(menu), update_item);

	gtk_widget_show(header_item);
	gtk_widget_show(update_item);

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

static void plugin_destructor(Plugin *p)
{
	/* TODO Remove this */
	--instance_cnt;

	/* Disconnect the timer. */
	g_source_remove(((kano_updater_plugin_t *)p->priv)->timer);

	kano_updater_plugin_t *plugin = (kano_updater_plugin_t *)p->priv;
	g_free(plugin);
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
PluginClass kano_updates_plugin_class = {
	// this is a #define taking care of the size/version variables
	PLUGINCLASS_VERSIONING,

	// type of this plugin
	type : "kano_updates",
	name : N_("Kano Updates"),
	version: "1.0",
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
