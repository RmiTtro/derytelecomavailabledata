//----------------------------------------------------------------------
// Imports
//----------------------------------------------------------------------
const GLib = imports.gi.GLib;
const Mainloop = imports.mainloop;
const Lang = imports.lang;

const Settings = imports.ui.settings;
const Applet = imports.ui.applet;
const Util = imports.misc.util;



//----------------------------------------------------------------------
// Constants
//----------------------------------------------------------------------
const UUID = "derytelecomavailabledata@remi.tetreault"
const PYTHON_SCRIPT_NAME = "/derytelecomextranetquery.py";




//----------------------------------------------------------------------
// Logging
//----------------------------------------------------------------------

function log(message) {
    global.log(UUID + ": " + message)
}

function logError(error) {
    global.logError(UUID + ": " + error)
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
        
        this.applet_on_panel = true;
        
        this.loop();
    },
    
    
    
    get_available: function() {
        // Let python handle the dirty work ;)
        Util.spawn_async(
            [
                'python', 
                this.metadata["path"]+PYTHON_SCRIPT_NAME, 
                this.username, this.password
            ], 
            Lang.bind(this, this.update_label)
        );
        
    },
    
    
    
    update_label: function(response)
    {
        let new_label = "Error";

        //remove newline
        response = response.replace(/(\r\n|\n|\r)/gm, "")
        
        if(response != "")
        {
             new_label = response;
        }
        else
        {
            logError("Nothing retrieved, please verify the user "    +
                     "credentials provided in the configuration of " +
                     "this applet");
        }
        
        this.set_applet_label(new_label);
    
    },
    
    
    
    loop: function()
    {
        // The loop must stop if the applet is not on the pannel
        if(this.applet_on_panel)
        {
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
    
    
    
    on_settings_changed: function()
    {
        // Nothing here for now
        
    },
    
    
    
    on_applet_removed_from_panel: function()
    {
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
    return new MyApplet(metadata, 
                        orientation, 
                        panel_height, 
                        instance_id);
}

