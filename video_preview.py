from moviepy.editor import VideoFileClip

def main():
    # Load your video clips
    clip1 = VideoFileClip("running.mp4")
    clip2 = VideoFileClip("loading.mp4")

    # Display the first video
    clip1.preview()

    # Display the second video
    clip2.preview()

if __name__ == "__main__":
    main()
