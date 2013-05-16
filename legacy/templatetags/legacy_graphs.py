from django import template
from django.template import Context, Template

register = template.Library()

IGNORE_TABLES = ['AccelerometerProbe', 'GyroscopeProbe', 'MagneticFieldProbe', 'PressureProbe', 'user_data', 'window1',  'window2',  'window3', 'CallHistoryFeature'
                 'RunningSoftwareProbe.RUNNING_TASKS', 'SoftwareInformationProbe.INSTALLED_APPS', 'WifiAccessPointsProbe.ACCESS_POINTS', 
                 'WifiAccessPointsProbe.ArrayValues', 'RunningSoftwareProbe.RUNNING_TASKS' ]

TEMPLATE_MAP = {
    'BatteryProbe': 'legacy_battery_graph.html',
    'RobotHealthProbe': 'legacy_health_graph.html',
    'RunningSoftwareProbe': 'legacy_software_graph.html',
    'SoftwareInformationProbe': 'legacy_installed_graph.html',
    'WeatherUndergroundFeature': 'legacy_weather_graph.html',
    'SunriseSunsetFeature': 'legacy_sunrise_graph.html',
    'WifiAccessPointsProbe': 'legacy_wifi_graph.html',
    'AccelerometerProbe.ArrayValues': 'legacy_accel_graph.html',
    'GyroscopeProbe.ArrayValues': 'legacy_gyro_graph.html',
    'MagneticFieldProbe.ArrayValues': 'legacy_magnet_graph.html',
    'PressureProbe.ArrayValues': 'legacy_pressure_graph.html',
    'RandomNoiseProbe': 'legacy_noise_graph.html'
}

def do_legacy_graph(parser, token):
    try:
        tag_name, graph_name, index = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a two arguments" % token.contents.split()[0])

    return LegacyGraphNode(graph_name, index)

class LegacyGraphNode(template.Node):
    def __init__(self, table_def, index):
        self.table_def = template.Variable(table_def)
        self.index = template.Variable(index)
    
    def render(self, context):
        table = self.table_def.resolve(context)
        index = self.index.resolve(context)
        
        t = None

        if table['name'] in IGNORE_TABLES:
            return ''
        elif table['name'] in TEMPLATE_MAP:
            t = template.loader.get_template(TEMPLATE_MAP[table['name']])
        else:
            t = template.loader.get_template('generic_table.html')

        return t.render(Context({'table': table, 'index': index}, autoescape=context.autoescape))

register.tag('legacy_graph', do_legacy_graph)