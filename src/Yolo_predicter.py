import os
import glob
import shutil
from src.config import tmp_dir,OVERLAP,XLIM,SIGNAL_TYPE,darknet_dir,predictions_file_name
from multiprocessing import Pool 
import matplotlib.pyplot as plt

class Yolo_predicter():
    def __init__(self,recording,replay,demo):
        self.recording = recording
        self.replay = replay
        self.predicted = False
        self.demo = demo
        
    @property
    def prediction_path(self):        
        files = ""

        
        if not self.predicted:
            if not self.replay:
                # Delete the previous tmp files
                for f in glob.iglob(f"{tmp_dir}*"):
                    os.remove(f)
                self.recording.signal.save_signal_to_tmp()
                self.generate_image_from_signal()
                
            for image in glob.iglob(f"{tmp_dir}*.png"):
                files += f"{image}\n"
                
            os.chdir(darknet_dir)
            
            with open("generate.txt", "w+") as f:
                f.write(files)

            if not self.demo and not self.replay:
                print("Running YOLO on signal. This may take a long time depending on GPU/CPU and length of recording")
                os.system((f"./darknet detector test ../obj.data ../yolo-obj.cfg ../yolo-obj_last.weights -dont_show -ext_output < generate.txt > {predictions_file_name}"))
                print("Done")
                
            if self.demo:
                print("Not implemented yet")
                assert(False)
                
            self.predicted = True
        return f"{darknet_dir}{predictions_file_name}"
            
        
    def plot_and_write_interval(self,params):
        signal,start = params
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xlim(start, start + XLIM)
        fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        ax.set_ylim(-1, 1)
        ax.plot(signal.index, signal[SIGNAL_TYPE])
        fig.savefig(f"{tmp_dir}{start}.png")
        plt.close()
        
        
    def generate_image_from_signal(self):
        """
        Plots images from the signal dataframe in a predictable way. Starts a new image for every OVERLAP/10 seconds to map the whole recording
        """    
        print("Generating image from signal")
        signal = self.recording.signal.signal
        with Pool(8) as pool:
            pool.map(self.plot_and_write_interval,zip([signal for i in range(0, len(signal), OVERLAP)],[i for i in range(0, len(signal), OVERLAP)]))
        print("Generated images")
        
        # TODO Create stats showing how far along we are currently. Probably more optimizing and finetuning?

