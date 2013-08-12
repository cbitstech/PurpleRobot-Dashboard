from django import template
from django.utils.datastructures import SortedDict

register = template.Library()

@register.filter(name='dict_sort')
def listsort(value):
    if isinstance(value, dict):
        new_dict = SortedDict()
        key_list = value.keys()
        key_list.sort()
        
        for key in key_list:
            new_dict[key] = value[key]
        return new_dict
    elif isinstance(value, list):
        new_list = list(value)
        new_list.sort()
        return new_list
    else:
        return value
    
    listsort.is_safe = True

@register.filter
def keyvalue(dict, key):
    try:
        return dict[key]
    except KeyError:
        pass
        
    return None

@register.filter
def clean_var_name(name):    
    return name.replace('FEATURE_VALUE_DT_', '').replace('R1', '')
