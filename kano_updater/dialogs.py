#!/usr/bin/env python

# dialogs.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango
from kano.gtk3.scrolled_window import ScrolledWindow
from kano.gtk3 import kano_dialog
from kano_updater.utils import add_text_to_end


def show_results(msg_upgraded, msg_added, msg_removed, debian_err_packages,
                 appstate_after_nonclean, python_ok, python_err):

    # Create Gtk textiew with markdown
    text_view = Gtk.TextView()
    text_view.set_margin_top(10)
    text_view.set_margin_bottom(20)
    text_view.set_margin_left(20)
    text_view.set_margin_right(20)
    text_buffer = text_view.get_buffer()
    bold_tag = text_buffer.create_tag("bold", weight=Pango.Weight.BOLD)

    scrolled_window = ScrolledWindow()
    scrolled_window.apply_styling_to_widget()
    scrolled_window.add_with_viewport(text_view)
    scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled_window.set_size_request(400, 200)

    result_dialog = kano_dialog.KanoDialog("Update result", "",
                                           widget=scrolled_window,
                                           global_style=True)
    result_dialog.dialog.set_icon_name("kano-updater")
    result_dialog.dialog.set_title("Kano Updater")

    if msg_upgraded:
        text = "\nApps upgraded:\n"
        add_text_to_end(text_buffer, text, bold_tag)
        add_text_to_end(text_buffer, msg_upgraded)

    if msg_added:
        text = "\nApps added:\n"
        add_text_to_end(text_buffer, text, bold_tag)
        add_text_to_end(text_buffer, msg_added)

    if msg_removed:
        text = "\nApps removed:\n"
        add_text_to_end(text_buffer, text, bold_tag)
        add_text_to_end(text_buffer, msg_removed)

    if debian_err_packages:
        text = "\nApps with errors:\n"
        add_text_to_end(text_buffer, text, bold_tag)
        msg_error = "{}\n".format('\n'.join(debian_err_packages))
        add_text_to_end(text_buffer, msg_error)

    if appstate_after_nonclean:
        text = "\nApps with non-clean state:\n"
        add_text_to_end(text_buffer, text, bold_tag)

        non_clean_list = '\n'.join(appstate_after_nonclean.iterkeys())
        msg_non_clean_list = non_clean_list + "\n"
        add_text_to_end(text_buffer, msg_non_clean_list)

    if python_ok:
        text = "\nPython modules upgraded:\n"
        add_text_to_end(text_buffer, text, bold_tag)

        python_modules = "{}\n".format('\n'.join(python_ok))
        add_text_to_end(text_buffer, python_modules)

    if python_err:
        text = "\nPython modules with error:\n"
        add_text_to_end(text_buffer, text, bold_tag)

        err_list = '\n'.join(python_err)
        msg_python_err = err_list + "\n"
        add_text_to_end(text_buffer, msg_python_err)

    if not (msg_upgraded or msg_added or msg_removed or debian_err_packages or
       appstate_after_nonclean or python_ok or python_err):
        add_text_to_end(text_buffer, "No updates needed this time.", bold_tag)

    result_dialog.run()
    while Gtk.events_pending():
        Gtk.main_iteration()


def show_reboot_dialog():
    rd_title = "Update successful!"
    rd_desc = "Now we just need to do a quick reboot. See you in a minute!"
    reboot_dialog = kano_dialog.KanoDialog(rd_title, rd_desc)

    reboot_dialog.run()
    while Gtk.events_pending():
        Gtk.main_iteration()
