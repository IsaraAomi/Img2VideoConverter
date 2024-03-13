import os, sys, argparse
import subprocess
from argparse import Namespace

import cv2
import numpy as np
from tqdm import tqdm
from PIL import Image
from moviepy.editor import VideoFileClip

class Img2VideoConverter():

    def __init__(self) -> None:
        self.SHORT_PROGRESS_BAR = "{l_bar}{bar:20}{r_bar}{bar:-10b}"
        self.SEPARATOR = "-"*60
        self.VIDEO_FPS = 60
        self.VIDEO_EXT = ".mp4"

        self.args = self.get_args()
        self.input_dir = self.args.input_dir
        self.output_dir = self.args.output_dir
        self.output_file_name = self.args.output_file_name
        self.output_video_tmp_path = os.path.join(self.output_dir, self.output_file_name + "_tmp" + self.VIDEO_EXT)
        self.output_video_path = os.path.join(self.output_dir, self.output_file_name + self.VIDEO_EXT)
        self.video_width = self.args.video_width
        self.interval = self.args.interval

        self.img_list = None

    def get_args(
            self,
            input_dir:str=None,
            output_dir:str=None,
            output_file_name:str="animation",
            video_width:int=720,
            interval:float=0.5,
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
        parser.add_argument("--output-file-name",
                            type=str, default=output_file_name,
                            help="Output File Name")
        parser.add_argument("--video-width",
                            type=int, default=video_width,
                            help="Video Width")
        parser.add_argument("--interval",
                            type=float, default=interval,
                            help="Interval")
        args = parser.parse_args()
        return args

    def show_args(self) -> None:
        print(f"[INFO] args info")
        print(f"[INFO] {self.SEPARATOR}")
        print(f"[INFO]     input_dir        : {self.input_dir}")
        print(f"[INFO]     output_dir       : {self.output_dir}")
        print(f"[INFO]     output_file_name : {self.output_file_name}")
        print(f"[INFO]     video_width      : {self.video_width}")
        print(f"[INFO]     interval         : {self.interval}")
        print(f"[INFO] {self.SEPARATOR}")

    def load_img(self, ext:str=".png") -> None:
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

    def show_img_list(self) -> None:
        print(f"{self.img_list}")

    def create_mp4(self) -> None:
        dpath = self.output_dir
        video_width = self.video_width
        if dpath is None:
            dpath = "."
        if not os.path.exists(dpath):
            os.makedirs(dpath)
        first_image = self.__read_img_without_metadata(self.img_list[0])
        img_height, img_width, _ = first_image.shape
        aspect = img_width / img_height
        video_height = int(video_width / aspect)
        print(f"[INFO] original image size: (height, width)=({img_height}, {img_width})")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_video_tmp_path, fourcc, self.VIDEO_FPS, (video_width, video_height))

        with tqdm(self.img_list, desc="[INFO] processing", bar_format=self.SHORT_PROGRESS_BAR) as t:
            for file in t:
                image = self.__read_img_without_metadata(file)
                image = cv2.resize(image, (video_width, video_height))
                for _ in range(int(self.VIDEO_FPS * self.interval)):
                    out.write(image)

        out.release()
    
    def convert_video_for_X(self):
        video_clip = VideoFileClip(self.output_video_tmp_path)
        print(f"[INFO] converting video for X")
        video_clip.write_videofile(self.output_video_path, codec='libx264', logger=None)

        cmd = ["rm", self.output_video_tmp_path]
        subprocess.run(cmd)

    def __read_img_without_metadata(self, file_path:str) -> None:
        image = Image.open(file_path)
        image_without_metadata = image.copy()
        image.close()
        image_data = cv2.cvtColor(np.array(image_without_metadata), cv2.COLOR_RGB2BGR)
        if image_data is None:
            print(f"[ERROR] failed to load image: {file_path}")
            sys.exit(1)
        return image_data

    def show_video_info(self, file_path:str) -> None:
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
    converter.load_img()
    converter.create_mp4()
    converter.show_video_info(converter.output_video_tmp_path)
    converter.convert_video_for_X()
    converter.show_video_info(converter.output_video_path)

if __name__ == '__main__':
    main()
