//=============================================================================
// derytelecomavailabledata
//
// Copyright(c) 2016 Rémi Tétreault <tetreault.remi@gmail.com>
// MIT Licensed, see LICENSE for more details.
//=============================================================================


//----------------------------------------------------------------------
// Imports
//----------------------------------------------------------------------
const GLib = imports.gi.GLib;
const Gio = imports.gi.Gio;
const Mainloop = imports.mainloop;
const Lang = imports.lang;

const Settings = imports.ui.settings;
const Applet = imports.ui.applet;
const Util = imports.misc.util;



//----------------------------------------------------------------------
// Constants
//----------------------------------------------------------------------
const PYTHON_SCRIPT_NAME = "derytelecomextranetquery";

const G_SPAWN_EXIT_ERROR =  GLib.spawn_exit_error_quark ();
const G_SPAWN_ERROR = GLib.spawn_error_quark ();




//----------------------------------------------------------------------
// Custom Spawn
//----------------------------------------------------------------------
// Spawn the program in argv and call the callback when the program
// return an exit code. The exit code is passed to the callback.
function spawn_async(argv, callback) {
    try {
        var [success, pid] =
            GLib.spawn_async(null, argv, null,
                             GLib.SpawnFlags.SEARCH_PATH
                             | GLib.SpawnFlags.DO_NOT_REAP_CHILD
                             | GLib.SpawnFlags.STDOUT_TO_DEV_NULL
                             | GLib.SpawnFlags.STDERR_TO_DEV_NULL,
                             null);
    } catch (err) {
        Util._handleSpawnError(argv[0], err);
    }


    if (success) {
        GLib.child_watch_add(GLib.PRIORITY_DEFAULT_IDLE, pid,
            function (pid, status) {
                var is_fatal_error = false;
                var exitcode = 0;

                try {
                    GLib.spawn_check_exit_status(status);
                } catch(err) {
                    if (err instanceof GLib.Error &&
                            err.domain === G_SPAWN_EXIT_ERROR) {
                        exitcode = err.code;
                    } else {
                        Util._handleSpawnError(argv[0], err);
                        is_fatal_error = true;
                    }
                }

                if (!is_fatal_error) {
                    callback(exitcode);
                }

                GLib.spawn_close_pid(pid);
            }
        );
    }
}



// Spawn the program in argv and call the callback when the program
// return an exit code. The exit code is passed to the callback and if
// its value is 0, the stdout of the program is also passed to the
// callback. If the value of the exit code is different then 0, pass
// stderr instead.
function spawn_async_with_pipes(argv, callback) {
    try {
        var [success, pid, in_fd, out_fd, err_fd] =
            GLib.spawn_async_with_pipes(null, argv, null,
                                        GLib.SpawnFlags.SEARCH_PATH
                                        | GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                                        null);
    } catch (err) {
        Util._handleSpawnError(argv[0], err);
    }


    if (success) {
        GLib.child_watch_add(GLib.PRIORITY_DEFAULT_IDLE, pid,
            function (pid, status) {
                var out_or_err = null;
                var is_fatal_error = false;
                var exitcode = 0;

                try {
                    GLib.spawn_check_exit_status(status);
                } catch(err) {
                    if (err instanceof GLib.Error &&
                            err.domain === G_SPAWN_EXIT_ERROR) {
                        exitcode = err.code;
                    } else {
                        Util._handleSpawnError(argv[0], err);
                        is_fatal_error = true;
                    }
                }

                if (!is_fatal_error) {
                    let fd = (exitcode === 0) ? out_fd : err_fd;
                    let reader = new Gio.DataInputStream({
                        base_stream: new Gio.UnixInputStream({fd: fd})
                    });

                    [out_or_err] = reader.read_until("", null);
                    callback(exitcode, out_or_err);
                }

                try {
                    GLib.close(in_fd);
                    GLib.close(out_fd);
                    GLib.close(err_fd);
                } catch(err) {
                    // Do nothing if there is an error, because we need to
                    // close the pid
                }

                GLib.spawn_close_pid(pid);
            }
        );
    }
}



//----------------------------------------------------------------------
// Logging
//----------------------------------------------------------------------
// UUID is defined in main
function log(message) {
    global.log(UUID + ": " + message);
}

function logError(error) {
    global.logError(UUID + ": " + error);
}



//----------------------------------------------------------------------
// MyApplet
//----------------------------------------------------------------------


function MyApplet(metadata, orientation, panel_height, instance_id) {
    this._init(metadata, orientation, panel_height, instance_id);
}


MyApplet.prototype = {
    __proto__: Applet.TextApplet.prototype,


    _init: function(metadata, orientation, panel_height, instance_id) {
        Applet.TextApplet.prototype._init.call(this,
                                               orientation,
                                               panel_height,
                                               instance_id);
        this.metadata = metadata;

        this.settings = new Settings.AppletSettings(this,
                                                    metadata["uuid"],
                                                    instance_id);

        this.settings.bindProperty(Settings.BindingDirection.IN,
                                   "username",
                                   "username",
                                   this.on_settings_changed,
                                   null);

        this.settings.bindProperty(Settings.BindingDirection.IN,
                                   "password",
                                   "password",
                                   this.on_settings_changed,
                                   null);

        this.settings.bindProperty(Settings.BindingDirection.IN,
                                   "update_delay_minutes",
                                   "update_delay_minutes",
                                   this.on_settings_changed,
                                   null);

        this.settings.bindProperty(Settings.BindingDirection.IN,
                                  "do_autologin",
                                  "do_autologin",
                                  this.on_settings_changed,
                                  null);

        this.settings.bindProperty(Settings.BindingDirection.IN,
                                "ok_color",
                                "ok_color",
                                this.on_settings_changed,
                                null);

        this.settings.bindProperty(Settings.BindingDirection.IN,
                                "error_color",
                                "error_color",
                                this.on_settings_changed,
                                null);

        this.applet_on_panel = true;
        this.clicked = false;
        this.set_applet_label("Error");
        this.loop();
    },



    get_available: function() {
        // Let python handle the dirty work ;)
        spawn_async_with_pipes(
            [
                'python',
                PYTHON_SCRIPT_PATH,
                "get",
                this.username, this.password
            ],
            Lang.bind(this, this.update_label)
        );
    },



    update_label: function(exitcode, out_or_err) {
        if (this.check_exitcode(exitcode, out_or_err)) {
            let new_label = out_or_err.replace(/(\r\n|\n|\r)/gm, "");
            this._applet_label.set_style("color:" + this.ok_color);
            this.set_applet_label(new_label);
        } else {
            this._applet_label.set_style("color:" + this.error_color);
        }
    },



    check_exitcode: function(exitcode, out_or_err) {
        switch(exitcode) {
            case 0:
                return true;
                break;

            case 1:
            case 2:
                logError("error calling the python program: "
                         + PYTHON_SCRIPT_NAME);
                break;


            default:
                logError(out_or_err);
        }

        return false;
    },



    loop: function() {
        // The loop must stop if the applet is not on the pannel
        if (this.applet_on_panel) {
            this.get_available();

            Mainloop.timeout_add_seconds(
                this.update_delay_minutes * 60,
                Lang.bind(this, this.loop)
            );
        }

        // For when this method is used as a callback for
        // Mainloop.timeout_add_seconds
        // Returning false mean whe don't want the
        // Mainloop.timeout_add_seconds from which the call is from to
        // automatically create another timeout
        // We want to keep control on the timeout creation since
        // the user can change the delay in the config of this applet
        return false;
    },



    on_settings_changed: function() {
        // Nothing here for now

    },


    on_applet_clicked: function() {
        // The clicked attribute is to make sure that multiple click on the
        // applet wont break everything
        if (!this.clicked) {
            this.clicked = true;
            let args = [
                'python',
                PYTHON_SCRIPT_PATH,
                "open"
            ]

            if (this.do_autologin) {
                args.push(this.username, this.password)
            }


            spawn_async(args, Lang.bind(this, function () {
                this.clicked = false;
            }));
        }
    },



    on_applet_removed_from_panel: function() {
        // Timeouts created using Mainloop.timeout_add_seconds does not
        // stop automatically when the applet is removed from the panel
        // This flag is used to stop those timeouts
        this.applet_on_panel = false;
    }
}


//----------------------------------------------------------------------
// Main
//----------------------------------------------------------------------
function main(metadata, orientation, panel_height, instance_id) {
    UUID = metadata["uuid"];
    PYTHON_SCRIPT_PATH = metadata["path"] + "/" + PYTHON_SCRIPT_NAME;

    return new MyApplet(metadata,
                        orientation,
                        panel_height,
                        instance_id);
}
