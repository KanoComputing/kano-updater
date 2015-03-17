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
#include <pwd.h>

#include <kdesk-hourglass.h>

#include "parson/parson.h"

/* Icon file paths */
#define NO_UPDATES_ICON_FILE \
	"/usr/share/kano-updater/images/widget-no-updates.png"
#define UPDATES_AVAILABLE_ICON_FILE \
	"/usr/share/kano-updater/images/widget-updates-available.png"
#define DOWNLOADING_UPDATES_ICON_FILE \
	"/usr/share/kano-updater/images/widget-downloading-updates.png"
#define UPDATES_DOWNLOADED_ICON_FILE \
	"/usr/share/kano-updater/images/widget-updates-downloaded.png"

#define UPDATE_STATUS_FILE "/var/cache/kano-updater/status.json"

#define CHECK_FOR_UPDATES_CMD "sudo /usr/bin/kano-updater check --gui"
#define DOWNLOAD_CMD "sudo /usr/bin/kano-updater download --low-prio"
#define INSTALL_CMD "sudo /usr/bin/kano-updater install --gui"
#define SOUND_CMD "/usr/bin/aplay /usr/share/kano-media/sounds/kano_open_app.wav"

#define PLUGIN_TOOLTIP _("Kano Updater")

#define POLL_INTERVAL (10 * 60 * 1000) /* 10 minutes in microseconds*/
#define CHECK_INTERVAL 60*60*24

#define FIFO_FILENAME ".kano-notifications.fifo"

#define MAX_STATE_LENGTH 20
#define IS_IN_STATE(plugin_data, s) \
	(g_strcmp0(plugin_data->state, s) == 0)

#define SET_STATE(plugin_data, s) do { \
	g_strlcpy(plugin_data->prev_state, plugin_data->state, MAX_STATE_LENGTH); \
	g_strlcpy(plugin_data->state, s, MAX_STATE_LENGTH); \
	} while(0)

#define UPDATES_AVAILABLE_NOTIFICATION \
	"{" \
		"\"title\": \"New Updates Available\"," \
		"\"byline\": \"Click here to download the them.\"," \
		"\"image\": \"/usr/share/kano-updater/images/notification-updates-available.png\"," \
		"\"sound\": null," \
		"\"type\": \"small\"," \
		"\"command\": \"sudo kano-updater download\"" \
	"}\n"

#define UPDATES_DOWNLOADED_NOTIFICATION \
	"{" \
		"\"title\": \"Download Complete\"," \
		"\"byline\": \"Time to power up!\"," \
		"\"image\": \"/usr/share/kano-updater/images/notification-updates-downloaded.png\"," \
		"\"sound\": null," \
		"\"type\": \"small\"," \
		"\"command\": \"sudo kano-updater install --gui\"" \
	"}\n"

typedef struct {
	GFile *status_file;
	GFileMonitor *monitor;

	gchar *state;
	gchar *prev_state;
	int last_update;
	int last_check;

	GtkWidget *icon;

	guint timer;

	LXPanel *panel;
} kano_updater_plugin_t;

static gboolean show_menu(GtkWidget *, GdkEventButton *,
			  kano_updater_plugin_t *);
static void selection_done(GtkWidget *);
static gboolean update_status(kano_updater_plugin_t *);
static gboolean check_for_updates(kano_updater_plugin_t *);

static void plugin_destructor(gpointer user_data);
static void menu_pos(GtkMenu *menu, gint *x, gint *y, gboolean *push_in,
                     GtkWidget *widget);

void file_monitor_cb(GFileMonitor *monitor, GFile *first, GFile *second,
		     GFileMonitorEvent event, gpointer user_data);

static GtkWidget *plugin_constructor(LXPanel *panel, config_setting_t *settings)
{
	/* allocate our private structure instance */
	kano_updater_plugin_t *plugin_data = g_new0(kano_updater_plugin_t, 1);

	plugin_data->panel = panel;

	plugin_data->state = g_new0(gchar, MAX_STATE_LENGTH);
	plugin_data->prev_state = g_new0(gchar, MAX_STATE_LENGTH);
	plugin_data->last_update = 0;
	plugin_data->last_check = 0;

	GtkWidget *icon = gtk_image_new_from_file(NO_UPDATES_ICON_FILE);
	plugin_data->icon = icon;

	/* need to create a widget to show */
	GtkWidget *pwid = gtk_event_box_new();
	lxpanel_plugin_set_data(pwid, plugin_data, plugin_destructor);

	/* set border width */
	gtk_container_set_border_width(GTK_CONTAINER(pwid), 0);

	/* add the label to the container */
	gtk_container_add(GTK_CONTAINER(pwid), GTK_WIDGET(icon));

	/* our widget doesn't have a window... */
	gtk_widget_set_has_window(pwid, FALSE);


	gtk_signal_connect(GTK_OBJECT(pwid), "button-press-event",
			   GTK_SIGNAL_FUNC(show_menu), plugin_data);


	/* Set a tooltip to the icon to show when the mouse sits over the it */
	GtkTooltips *tooltips;
	tooltips = gtk_tooltips_new();
	gtk_tooltips_set_tip(tooltips, GTK_WIDGET(icon), PLUGIN_TOOLTIP, NULL);

	gtk_widget_set_sensitive(icon, TRUE);

	update_status(plugin_data);

	plugin_data->timer = g_timeout_add(POLL_INTERVAL,
					   (GSourceFunc) check_for_updates,
					   (gpointer) plugin_data);

	/* show our widget */
	gtk_widget_show_all(pwid);

	/* Start watching the pipe for input. */
	plugin_data->status_file = g_file_new_for_path(UPDATE_STATUS_FILE);
	g_assert(plugin_data->status_file != NULL);

	plugin_data->monitor = g_file_monitor(plugin_data->status_file,
					      G_FILE_MONITOR_NONE, NULL, NULL);
	g_assert(plugin_data->monitor != NULL);
	g_signal_connect(plugin_data->monitor, "changed",
			 G_CALLBACK(file_monitor_cb), (gpointer) plugin_data);

	return pwid;
}

static void plugin_destructor(gpointer user_data)
{
	kano_updater_plugin_t *plugin_data = (kano_updater_plugin_t *)user_data;

	g_free(plugin_data->state);
	g_free(plugin_data->prev_state);

	g_object_unref(plugin_data->monitor);

	/* Disconnect the timer. */
	g_source_remove(plugin_data->timer);

	g_free(plugin_data);
}

void file_monitor_cb(GFileMonitor *monitor, GFile *first, GFile *second,
		     GFileMonitorEvent event, gpointer user_data)
{
	kano_updater_plugin_t *plugin_data = (kano_updater_plugin_t *)user_data;
	update_status(plugin_data);
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

static gboolean check_for_updates(kano_updater_plugin_t *plugin_data)
{
	int now = time(NULL);
	if ((now - plugin_data->last_check) >= CHECK_INTERVAL) {
	    launch_cmd(CHECK_FOR_UPDATES_CMD, NULL);
	}
    return TRUE;
}

/*
 * Resolve the path to the pipe file in the user's $HOME directory.
 *
 * WARNING: You're expected to g_free() the string returned.
 */
gchar *get_notifications_fifo_filename(void)
{
	struct passwd *pw = getpwuid(getuid());
	const char *homedir = pw->pw_dir;

	/* You are responsible for freeing the returned char buffer */
	int buff_len=strlen(homedir) + strlen(FIFO_FILENAME) + sizeof(char) * 2;
	gchar *fifo_filename = g_new0(gchar, buff_len);
	if (!fifo_filename) {
		return NULL;
	}
	else {
		g_strlcpy(fifo_filename, homedir, buff_len);
		g_strlcat(fifo_filename, "/", buff_len);
		g_strlcat(fifo_filename, FIFO_FILENAME, buff_len);
		return (fifo_filename);
	}
}

static void show_notification(gchar *spec)
{
	gchar *notif_pipe = get_notifications_fifo_filename();

	FILE *stream;
	stream = fopen(notif_pipe, "w");
	fprintf(stream, spec);
	fclose(stream);

	g_free(notif_pipe);
}

static gboolean read_status(kano_updater_plugin_t *plugin_data)
{
	JSON_Value *root_value = NULL;
	JSON_Object *root = NULL;

	root_value = json_parse_file(UPDATE_STATUS_FILE);
	if (json_value_get_type(root_value) == JSONObject) {
		root = json_value_get_object(root_value);

		SET_STATE(plugin_data, json_object_get_string(root, "state"));

		plugin_data->last_check = (int) json_object_get_number(root,
								 "last_check");
		plugin_data->last_update = (int) json_object_get_number(root,
								"last_update");

		json_value_free(root_value);
		return TRUE;
	}

	json_value_free(root_value);
	return FALSE;
}

static gboolean update_status(kano_updater_plugin_t *plugin_data)
{
	read_status(plugin_data);

	/* printf("%s lu%d lc%d\n", plugin_data->state,
				 plugin_data->last_update,
				 plugin_data->last_check); */

	if (IS_IN_STATE(plugin_data, "updates-available")) {
		gtk_image_set_from_file(GTK_IMAGE(plugin_data->icon),
						  UPDATES_AVAILABLE_ICON_FILE);

		if (g_strcmp0(plugin_data->prev_state, plugin_data->state) != 0)
			show_notification(UPDATES_AVAILABLE_NOTIFICATION);
	} else if (IS_IN_STATE(plugin_data, "downloading-updates")) {
		gtk_image_set_from_file(GTK_IMAGE(plugin_data->icon),
						DOWNLOADING_UPDATES_ICON_FILE);
	} else if (IS_IN_STATE(plugin_data, "updates-downloaded")) {
		gtk_image_set_from_file(GTK_IMAGE(plugin_data->icon),
						UPDATES_DOWNLOADED_ICON_FILE);

		if (g_strcmp0(plugin_data->prev_state, plugin_data->state) != 0)
			show_notification(UPDATES_DOWNLOADED_NOTIFICATION);
	} else {
		gtk_image_set_from_file(GTK_IMAGE(plugin_data->icon),
					NO_UPDATES_ICON_FILE);
	}

	return TRUE;
}

void download_clicked(GtkWidget *widget, gpointer data)
{
    /* Launch updater */
    launch_cmd(DOWNLOAD_CMD, "kano-updater");

    /* Play sound */
    launch_cmd(SOUND_CMD, NULL);
}

void install_clicked(GtkWidget *widget, gpointer data)
{
    /* Launch updater */
    launch_cmd(INSTALL_CMD, "kano-updater");

    /* Play sound */
    launch_cmd(SOUND_CMD, NULL);
}

void check_for_updates_clicked(GtkWidget *widget,
			       kano_updater_plugin_t *plugin_data)
{
	check_for_updates(plugin_data);
}

static void menu_add_item(GtkWidget *menu, gchar *label, gpointer activate_cb,
			  gpointer user_data, gboolean active)
{
	GtkWidget *item;
	item = gtk_menu_item_new_with_label(label);

	if (activate_cb)
		g_signal_connect(item, "activate",
				 G_CALLBACK(activate_cb), user_data);

	if (!active)
		gtk_widget_set_sensitive(item, FALSE);

	gtk_menu_append(GTK_MENU(menu), item);
	gtk_widget_show(item);
}

static gboolean show_menu(GtkWidget *widget, GdkEventButton *event,
		      kano_updater_plugin_t *plugin_data)
{
	GtkWidget *menu = gtk_menu_new();

	if (event->button != 1)
		return FALSE;

	update_status(plugin_data);

	/* Create the menu items */
	menu_add_item(menu, _("Kano Updater"), NULL, NULL, FALSE);

	if (IS_IN_STATE(plugin_data, "updates-available")) {
		menu_add_item(menu, _("Download updates"),
				G_CALLBACK(download_clicked), NULL, TRUE);
	} else if (IS_IN_STATE(plugin_data, "downloading-updates")) {
		menu_add_item(menu, _("Download in progress ..."),
			      NULL, NULL, FALSE);
	} else if (IS_IN_STATE(plugin_data, "updates-downloaded")) {
		menu_add_item(menu, _("Install updates"),
				G_CALLBACK(install_clicked), NULL, TRUE);
	} else if (IS_IN_STATE(plugin_data, "installing-updates")) {
		menu_add_item(menu, _("Installation in progress ..."),
			      NULL, NULL, FALSE);
	} else {
		menu_add_item(menu, _("No updates found"),
			      NULL, NULL, FALSE);
		menu_add_item(menu, _("Check again"),
				G_CALLBACK(check_for_updates_clicked),
				plugin_data, TRUE);
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
    kano_updater_plugin_t *plugin_data = lxpanel_plugin_get_data(widget);
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
    if (panel_get_orientation(plugin_data->panel) == GTK_ORIENTATION_HORIZONTAL) {
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
