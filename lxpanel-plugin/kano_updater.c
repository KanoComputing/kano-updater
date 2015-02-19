/*
 * kano_updater.c
 *
 * Copyright (C) 2014 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
 *
 */

#include <gtk/gtk.h>
#include <gdk/gdk.h>
#define GETTEXT_PACKAGE "kano-updater"
#include <glib/gi18n-lib.h>
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

#define CHECK_FOR_UPDATES_CMD "sudo /usr/bin/check-for-updates"
#define UPDATE_CMD "kdesk-blur 'sudo /usr/bin/kano-updater'"
#define SOUND_CMD "/usr/bin/aplay /usr/share/kano-media/sounds/kano_open_app.wav"

#define PLUGIN_TOOLTIP _("Kano Updater")

#define DAY 60*60*24

typedef struct {
	int last_update;
	int last_check;
	int update_available;

	GtkWidget *icon;

	guint timer;

	LXPanel *panel;
} kano_updater_plugin_t;

static gboolean show_menu(GtkWidget *, GdkEventButton *,
			  kano_updater_plugin_t *);
static void selection_done(GtkWidget *);
static gboolean update_status(kano_updater_plugin_t *);

static void plugin_destructor(gpointer user_data);
static void menu_pos(GtkMenu *menu, gint *x, gint *y, gboolean *push_in,
                     GtkWidget *widget);


static GtkWidget *plugin_constructor(LXPanel *panel, config_setting_t *settings)
{
	/* allocate our private structure instance */
	kano_updater_plugin_t *plugin = g_new0(kano_updater_plugin_t, 1);

	plugin->panel = panel;

	plugin->last_update = 0;
	plugin->last_check = 0;
	plugin->update_available = 0;

	GtkWidget *icon = gtk_image_new_from_file(DEFAULT_ICON_FILE);
	plugin->icon = icon;

	/* need to create a widget to show */
	GtkWidget *pwid = gtk_event_box_new();
	lxpanel_plugin_set_data(pwid, plugin, plugin_destructor);

	/* set border width */
	gtk_container_set_border_width(GTK_CONTAINER(pwid), 0);

	/* add the label to the container */
	gtk_container_add(GTK_CONTAINER(pwid), GTK_WIDGET(icon));

	/* our widget doesn't have a window... */
	gtk_widget_set_has_window(pwid, FALSE);


	gtk_signal_connect(GTK_OBJECT(pwid), "button-press-event",
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
	gtk_widget_show_all(pwid);

	return pwid;
}

static void plugin_destructor(gpointer user_data)
{
	kano_updater_plugin_t *plugin = (kano_updater_plugin_t *)user_data;

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

static void launch_cmd(const char *cmd, const char *appname)
{
	GAppInfo *appinfo = NULL;
	gboolean ret = FALSE;

	appinfo = g_app_info_create_from_commandline(cmd, NULL,
				G_APP_INFO_CREATE_NONE, NULL);

        if (appname) {
            kdesk_hourglass_start((char *) appname);
        }

        if (appinfo == NULL) {
            perror("Command lanuch failed.");
            if (appname) {
                kdesk_hourglass_end();
            }
            return;
	}

	ret = g_app_info_launch(appinfo, NULL, NULL, NULL);
	if (!ret) {
            perror("Command lanuch failed.");
            if (appname) {
                kdesk_hourglass_end();
            }
        }
}

static gboolean check_for_updates(kano_updater_plugin_t *plugin)
{
    launch_cmd(CHECK_FOR_UPDATES_CMD, NULL);
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
    /* Launch updater */
    launch_cmd(UPDATE_CMD, "kano-updater");

    /* Play sound */
    launch_cmd(SOUND_CMD, NULL);
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
	header_item = gtk_menu_item_new_with_label(_("Kano Updater"));
	gtk_widget_set_sensitive(header_item, FALSE);
	gtk_menu_append(GTK_MENU(menu), header_item);
	gtk_widget_show(header_item);

	if (plugin->update_available > 0) {
		update_item = gtk_menu_item_new_with_label(_("Update your system"));
		g_signal_connect(update_item, "activate",
				 G_CALLBACK(update_clicked), NULL);
		gtk_menu_append(GTK_MENU(menu), update_item);
		gtk_widget_show(update_item);
	} else {
		no_updates_item = gtk_menu_item_new_with_label(_("No updates found"));
		gtk_widget_set_sensitive(no_updates_item, FALSE);
		gtk_menu_append(GTK_MENU(menu), no_updates_item);
		gtk_widget_show(no_updates_item);

		check_item = gtk_menu_item_new_with_label(_("Check again"));
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
		       (GtkMenuPositionFunc) menu_pos, widget,
		       event->button, event->time);

	return TRUE;
}

static void selection_done(GtkWidget *menu)
{
    gtk_widget_destroy(menu);
}

static void menu_pos(GtkMenu *menu, gint *x, gint *y, gboolean *push_in,
                     GtkWidget *widget)
{
    int ox, oy, w, h;
    kano_updater_plugin_t *plugin = lxpanel_plugin_get_data(widget);
    GtkAllocation allocation;

    gtk_widget_get_allocation(GTK_WIDGET(widget), &allocation);

    gdk_window_get_origin(gtk_widget_get_window(widget), &ox, &oy);

    /* FIXME The X origin is being truncated for some reason, reset
       it from the allocaation. */
    ox = allocation.x;

#if GTK_CHECK_VERSION(2,20,0)
    GtkRequisition requisition;
    gtk_widget_get_requisition(GTK_WIDGET(menu), &requisition);
    w = requisition.width;
    h = requisition.height;

#else
    w = GTK_WIDGET(menu)->requisition.width;
    h = GTK_WIDGET(menu)->requisition.height;
#endif
    if (panel_get_orientation(plugin->panel) == GTK_ORIENTATION_HORIZONTAL) {
        *x = ox;
        if (*x + w > gdk_screen_width())
            *x = ox + allocation.width - w;
        *y = oy - h;
        if (*y < 0)
            *y = oy + allocation.height;
    } else {
        *x = ox + allocation.width;
        if (*x > gdk_screen_width())
            *x = ox - w;
        *y = oy;
        if (*y + h >  gdk_screen_height())
            *y = oy + allocation.height - h;
    }

    /* Debugging prints */
    /*printf("widget: x,y=%d,%d  w,h=%d,%d\n", ox, oy, allocation.width, allocation.height );
    printf("w-h %d %d\n", w, h); */

    *push_in = TRUE;

    return;
}

FM_DEFINE_MODULE(lxpanel_gtk, kano_updater)

/* Plugin descriptor. */
LXPanelPluginInit fm_module_init_lxpanel_gtk = {
    .name = N_("Kano Updater"),
    .description = N_("A reminder to keep your Kano OS up-to-date."),
    .new_instance = plugin_constructor,
    .one_per_system = FALSE,
    .expand_available = FALSE
};
