import os, sys, argparse
from argparse import Namespace

import cv2
import numpy as np
from tqdm import tqdm
from PIL import Image

class Img2VideoConverter():

    def __init__(self) -> None:
        self.SHORT_PROGRESS_BAR="{l_bar}{bar:20}{r_bar}{bar:-10b}"
        self.SEPARATOR="-"*40

        self.args = self.get_args()
        self.input_dir = self.args.input_dir
        self.output_dir = self.args.output_dir
        self.img_list = None

    def get_args(
            self,
            input_dir:str=None,
            output_dir:str=None,
            description=None
        ) -> Namespace:
        if description is None:
            description = "Img2VideoConverter"
        parser = argparse.ArgumentParser(description)
        parser.add_argument("--input-dir",
                            type=str, default=input_dir,
                            help="Input Directory")
        parser.add_argument("--output-dir",
                            type=str, default=output_dir,
                            help="Output Directory")
        args = parser.parse_args()
        return args

    def show_args(self):
        print(f"[INFO] args info")
        print(f"[INFO] {self.SEPARATOR}")
        print(f"[INFO]     input_dir  : {self.args.input_dir}")
        print(f"[INFO]     output_dir : {self.args.output_dir}")
        print(f"[INFO] {self.SEPARATOR}")

    def load_img(
            self,
            ext:str=".png"
        ) -> None:
        dpath = self.input_dir
        if not os.path.isdir(dpath):
            print(f"[ERROR] cannot find path: {dpath}")
            sys.exit(1)
        files_list = []
        for file in os.listdir(dpath):
            file_path = os.path.join(dpath, file)
            if os.path.isfile(file_path):
                if file.endswith(ext):
                    files_list.append(file_path)
        if not files_list:
            print(f"[ERROR] cannot find any file, search ext: {ext}")
            sys.exit(1)
        self.img_list = sorted(files_list)

    def show_img_list(self):
        print(f"{self.img_list}")

    def create_mp4(
            self,
            file_name="animation",
            frame_rate=2.0,
            video_width:int=480
        ) -> None:
        dpath = self.output_dir
        if dpath is None:
            dpath = "."
        if not os.path.exists(dpath):
            os.makedirs(dpath)
        first_image = self.__read_img_without_metadata(self.img_list[0])
        img_height, img_width, _ = first_image.shape
        aspect = img_width / img_height
        video_height = int(video_width / aspect)
        print(f"[INFO] original image size: (height, width)=({img_height}, {img_width})")

        output_file = os.path.join(dpath, file_name + ".mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, frame_rate, (video_width, video_height))

        with tqdm(self.img_list, desc="[INFO] processing", bar_format=self.SHORT_PROGRESS_BAR) as t:
            for file in t:
                # image = cv2.imread(file)
                image = self.__read_img_without_metadata(file)
                if image is None:
                    print(f"[ERROR] failed to load image: {file}")
                    sys.exit(1)
                image = cv2.resize(image, (video_width, video_height))
                out.write(image)

        out.release()
        self.__show_video_info(output_file)

    def __read_img_without_metadata(self, file_path):
        image = Image.open(file_path)
        image_without_metadata = image.copy()
        image.close()
        image_data = cv2.cvtColor(np.array(image_without_metadata), cv2.COLOR_RGB2BGR)
        return image_data

    def __show_video_info(self, file_path):
        cap = cv2.VideoCapture(file_path)
        print(f"[INFO] video info")
        print(f"[INFO] {self.SEPARATOR}")
        print(f"[INFO]     path   : {file_path}")
        print(f"[INFO]     width  : {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}")
        print(f"[INFO]     height : {int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        print(f"[INFO]     fps    : {int(cap.get(cv2.CAP_PROP_FPS))}")
        print(f"[INFO]     length : {cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)} [s]")
        print(f"[INFO] {self.SEPARATOR}")


def main():
    """
    - Args:
    - Returns:
    """    
    converter = Img2VideoConverter()
    converter.show_args()
    converter.load_img(ext=".png")
    converter.create_mp4()

if __name__ == '__main__':
    main()
