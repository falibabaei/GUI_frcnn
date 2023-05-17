import os
import tempfile
import zipfile
import numpy as np
import gradio as gr
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def api2gr_inputs(api_inp):
    """
    Transform DEEPaaS webargs to Gradio inputs.
    """
    inp_names = [i['name'] for i in api_inp]
    

    inp_types = {i['name']: i['type'] for i in api_inp}
    gr_inp = []
    for k, v in zip(inp_names, api_inp):
        
        if k == 'accept':
            continue
     
            
        if k in ['timestamp' ]:
           gr_inp.append( gr.inputs.Dropdown(choices=[],
                                     default=v.get('default', None),
                                     label=k,
                                     ) ) # could also be gr.inputs.
        
        
        elif 'enum' in v.keys() and v['type'] not  in ['boolean' ]:
         
                gr_inp.append(gr.inputs.Radio(choices=v['enum'],
                                     default=v.get('default', None),
                                     label=k))  # could also be gr.inputs.Radio()
         
        elif v['type'] in [ 'integer' ,'number', 'float']:
            if (v['type'] == 'integer') and {'minimum', 'maximum'}.issubset(v.keys()):
                gr_inp.append(gr.inputs.Slider(default=v.get('default', None),
                                       minimum=v.get('minimum', None),
                                       maximum=v.get('maximum', None),
                                       step=1,
                                       label=k))
            else:
                gr_inp.append(gr.inputs.Number(default=v.get('default', None),
                                       label=k))
        elif v['type'] in ['boolean' ]:
            gr_inp.append(gr.inputs.Checkbox(default=v.get('default', None),
                                     label=k))
        elif v['type'] in ['string' ]:
              gr_inp.append(gr.inputs.Textbox(default=v.get('default', None),                     
                                    label=k))
       
        elif v['type'] in ['file']:
            gr_inp.append( gr.inputs.File(type='file',# file_count="multiple",
                                      label='Input Files (FASTA format)'))
        else:
            raise Exception(f"UI does not support some of the input data types: `{k}` :: {v['type']}")
      
    return gr_inp, inp_names, inp_types


def api2gr_outputs(struct):
    """
    Transform DEEPaaS webargs to Gradio outputs.
    """
    gr_out = []
    for k, v in struct.items():


        if v['type'] == 'pdf':
            tmp = gr.outputs.File(type='file',
                                   label=k,
                                   accept='.pdf')
        elif v['type'] == 'json':
            tmp = gr.outputs.JSON(label=k)

        else:
            raise Exception(f"UI does not support some of the output data types: {k} [{v['type']}]")
        gr_out.append(tmp)
        
    return gr_out




def gr2api_input(params,inp_types):
    """
    Transform Gradio inputs to DEEPaaS webargs.
    """
    files={}
    for k, v in params.copy().items():

            if inp_types[k] == 'integer':
                params[k] = int(v)
            elif inp_types[k] == 'number':#float 
             params[k] = float(v)    
            elif inp_types[k] == 'string':
                 params[k]=f"{v}"
            elif inp_types[k] == 'boolean':
                 params[k] = v
            elif inp_types[k] in ['file'] and v!=None:
                    media = params.pop(k) 
                    path = media 
                    files[k] = open(path, 'rb')
                     
                  
    return params, files                    

def get_parameter_default(param_name, api_inp ):
    param_value = next((param["default"] for param in api_inp if param["name"] == param_name), None)
    return param_value