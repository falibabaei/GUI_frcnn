 
from pathlib import Path
from PIL import Image
from urllib.parse import urljoin
import click
import gradio as gr
import requests
import  utils
from io import BytesIO

gr.close_all()
GRADIO_SERVER = "0.0.0.0"
@click.command()
@click.option('--api_url',
              default='http://0.0.0.0:5000/',
              help='URL of the DEEPaaS API')
@click.option('--ui_port',
              default=8000,
              help='URL of the deployed UI')


def main(api_url, ui_port):
    """
    This module contains several functions that make calls to the deep API.
    Args:
        api_url: URL of the deep api.
        ui_port: port for GUI 

    """
    sess = requests.Session()
    r = sess.get(urljoin(api_url , 'swagger.json'))
    specs = r.json()
   
    pred_paths = [p for p in specs['paths'].keys() if p.endswith('predict/')]
    p = pred_paths[0]  # FIXME: we are only interfacing the first model found
    
    print(f'Parsing {Path(p).parent}')
    api_inp = specs['paths'][p]['post']['parameters']
    api_out = specs['paths'][p]['post']['produces']
    r = sess.get(f'{api_url}/{Path(p).parent}/')
  
    _, inp_names, inp_types=utils.api2gr_inputs(api_inp)
   
    def make_request(params,accept):
        """
         Receives parameters from the GUI and returns the JSON file resulting from calling the deep API.

         Args:
          params:  the parameters entered by the user in the GUI.
          accept: specifies the format of the resulting request.

        Returns:
          rc: the content of the response from the API.
         """    
        #convert GUI input to DEEPaaS webargs
        params, files=utils.gr2api_input(params,inp_types)           
        r = sess.post(urljoin(api_url,p), 
                  headers={'accept': accept},
                  params=params,
                  files=files,
                  verify=False)

        if r.status_code != 200:
            raise Exception(f'HTML {r.status_code} eror: {r}')
        
        return  r.content 

    
    def api_call(*args, **kwargs):
      """
      Receives the converted parameters from the GUI as arguments for the deep API,
         calls the API with the specified parameters, and loads the JSON file from the response.
  
      Args:
           args: The converted parameters from the GUI to deep API arguments.

      Returns:
        rc: A JSON file containing a list of predictions for each input file.
      """
      
      accept = api_out[0]
      timestamp = "2023-05-10_121810"
      imgsz = utils.get_parameter_default("imgsz", api_inp )
      device = utils.get_parameter_default("device", api_inp )
      square_img = utils.get_parameter_default("square_img", api_inp )
      trashhold=args[1]/100
      # Concatenating the variables 
      params = dict(zip(inp_names, (args[:1] + (timestamp,) +(trashhold,)
                                     +(imgsz,)+(device,)  + args[2:] + (square_img,))))
      buffer = make_request( params, accept)
      image = Image.open(BytesIO(buffer))
      return image
 
    gr_inp=[]
    gr_inp.append(gr.Image(type='filepath', file_count="multiple",
                                      label='Input an Image'))
    gr_inp.append(gr.Slider(default= 40,
                                       minimum=0.0,
                                       maximum=100,
                                       step=1,
                                       label='Threshold: adjust this parameter to visualize a bounding box based on a threshold value.'))
    gr_inp.append(gr.inputs.Checkbox(default=False,
                                     label='remove the label from the bounding box visualization'))
    
    output=gr.Image(type='pil', label='Image with bounding box')      
    project_description = "The model can predict the animal in the following classes: crab, small_fish, starfish, fish, jellyfish, and shrimp."    
    demo = gr.Interface(api_call, gr_inp, output,
                        title="Submarine Animal Detection",
                          description=project_description)   
 
    demo.launch(share=False,
                show_error=True,
                server_name=GRADIO_SERVER,
                server_port=ui_port)

    
if __name__== '__main__':
   
    main()
