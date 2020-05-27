import os

tmp_dir = f"{os.getcwd()}{os.sep}tmp{os.sep}"
tmp_signal_name = "last_file.npz"
XLIM = 90 * 10
OVERLAP = 45 * 10
SIGNAL_TYPE = "ABDO_RES"
darknet_dir = f"{os.getcwd()}{os.sep}darknet{os.sep}"
predictions_file_name = "predictions.txt"
main_folder = f"{os.getcwd()}{os.sep}"