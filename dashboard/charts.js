var swig  = require('swig');
var db = require('./database');

var ignoreList = ["AccelerometerProbe",
                  "MagneticFieldProbe",
                  "ProximityProbe",
                  "PressureProbe",
                  "LightProbe",
                  "GyroscopeProbe",
                  "TemperatureProbe",
                  "PressureProbe",
                  "SourceValue",
                  "AccelerometerSensorProbe",
                  "HardwareInfoProbe",
                  "BluetoothDevicesProbe.ArrayValues",
                  "ContinuousGyroscopeProbe",
                  "ContinuousAccelerometerProbe",
                  "ContinuousGyroscopeProbe.ArrayValues",
                  "WifiAccessPointsProbe.ArrayValues",
                  "js",
                  "ContinuousAccelerometerProbe.ArrayValues",
                  "ContinuousMagneticFieldProbe.ArrayValues",
                  "ContinuousMagneticFieldProbe",
                  "ContinuousPressureProbe",
                  "ContinuousPressureProbe.ArrayValues"];

function genericView(name, value)
{
    var view = {};
    view.name = name;
    view.value = value;
    
    view.render = function()
    {
        var tmpl = swig.compileFile('charts/generic.html');
        
        return tmpl.render({ view: view });
    };
    
    return view;
}

function templateView(name, value, template, properties)
{
    if (properties == null)
        properties = {};
        
    var view = genericView(name, value);

    properties['view'] = view;
    properties['name'] = name;
    properties['value'] = value;
    
    view.render = function()
    {
        var tmpl = swig.compileFile(template);
        
        return tmpl.render(properties);
    };

    return view;
}

exports.chartForObject = function(name, value)
{
    if (name === "RobotHealthProbe")
        return templateView(name, value, 'charts/spline.html', { columns: 'PENDING_COUNT', canvas: 'health' });
    else if (name === "BatteryProbe")
        return templateView(name, value, 'charts/spline.html', { columns: 'level', canvas: 'battery' });
    else if (name === "BluetoothDevicesProbe")
        return templateView(name, value, 'charts/spline.html', { columns: 'DEVICE_COUNT', canvas: 'bluetooth' });
    else if (name === "WifiAccessPointsProbe")
        return templateView(name, value, 'charts/spline.html', { columns: 'ACCESS_POINT_COUNT', canvas: 'wifi' });
    else if (name === "RunningSoftwareProbe")
        return templateView(name, value, 'charts/spline.html', { columns: 'RUNNING_TASK_COUNT', canvas: 'running_software' });
    else if (name === "SoftwareInformationProbe")
        return templateView(name, value, 'charts/spline.html', { columns: 'INSTALLED_APP_COUNT', canvas: 'installed_software' });
    else if (name === "VisibleSatelliteProbe")
        return templateView(name, value, 'charts/spline.html', { columns: 'SATELLITE_COUNT', canvas: 'satellite' });

    else if (name === "PressureProbe.ArrayValues")
        return templateView(name, value, 'charts/spline.html', { columns: 'PRESSURE', canvas: 'pressure' });
    else if (name === "ProximityProbe.ArrayValues")
        return templateView(name, value, 'charts/spline.html', { columns: 'DISTANCE', canvas: 'proximity' });
    else if (name === "LightProbe.ArrayValues")
        return templateView(name, value, 'charts/spline.html', { columns: 'LUX', canvas: 'light' });
    else if (name === "TemperatureProbe.ArrayValues")
        return templateView(name, value, 'charts/spline.html', { columns: 'TEMPERATURE', canvas: 'temperature' });

    else if (name === "AccelerometerProbe.ArrayValues")
        return templateView(name, value, 'charts/spline.html', { columns: 'X,Y,Z', canvas: 'accelerometer' });
    else if (name === "AccelerometerSensorProbe.ArrayValues") // Old Name
        return templateView(name, value, 'charts/spline.html', { columns: 'X,Y,Z', canvas: 'accelerometer_sensor' });
    else if (name === "GyroscopeProbe.ArrayValues")
        return templateView(name, value, 'charts/spline.html', { columns: 'X,Y,Z', canvas: 'gyroscope' });
    else if (name === "MagneticFieldProbe.ArrayValues")
        return templateView(name, value, 'charts/spline.html', { columns: 'X,Y,Z', canvas: 'magnetic' });

    else if (name === "CommunicationLogProbe")
        return templateView(name, value, 'charts/spline.html', { columns: 'CALL_INCOMING_COUNT,CALL_MISSED_COUNT,CALL_OUTGOING_COUNT,SMS_INCOMING_COUNT,SMS_OUTGOING_COUNT', canvas: 'comm_log' });

    else if (name === "ScreenProbe")
        return templateView(name, value, 'charts/screen.html', null);
    
    // TODO: Create renderers
    
    else if (name === "NetworkProbe")
        return null;
    else if (name === "DeviceInUseFeature")
        return null;
    else if (name === "Current JS Time")
        return null;
    else if (name === "WifiAccessPointsProbe.ACCESS_POINTS")
        return null;
    else if (name === "BluetoothDevicesProbe.DEVICES")
        return null;
    else if (name === "SoftwareInformationProbe.INSTALLED_APPS")
        return null;
    else if (name === "CommunicationLogProbe.PHONE_CALLS")
        return null;
    else if (name === "BluetoothDevicesProbe.DEVICES")
        return null;
    else if (name === "HardwareInformationProbe")
        return null;
    else if (name === "RunningSoftwareProbe.RUNNING_TASKS")
        return null;
    else if (name === "TelephonyProbe")
        return null;
    else if (name === "HardwareInformationProbe")
        return null;
    else if (name === "CallStateProbe")
        return null;
    
    else if (ignoreList.indexOf(name) != -1)
        return null;

    return genericView(name, value);
};
