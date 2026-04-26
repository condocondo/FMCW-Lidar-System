import glob
from PIL import Image
c = 3*(10**8) #m/s


def get_BW_Lambda_range(center_lambda=1550*(10**-9), total_lambda=100*(10**-9)):
    BW = c*total_lambda/(center_lambda**2)
    return BW  # Hz


def get_Lambda_range_BW(center_lambda=1550*(10**-9), BW=100*(10**-9)):
    lambda_range = (BW*(center_lambda**2)/c)*(10**12)
    return lambda_range # pm


def make_gif(frame_folder):
    frames = [Image.open(image) for image in glob.glob(f"{frame_folder}/*.png")]
    # frames = [Image.open(image) for image in sorted(glob.glob(f"{frame_folder}/*.png"))]
    frame_one = frames[0]
    frame_one.save("discretized_first_test.gif", format="GIF", append_images=frames,
                   save_all=True, duration=100, loop=0)

if __name__ == "__main__":
    # make_gif("images/")
    BW = get_BW_Lambda_range()
    print(BW*(10**-9))