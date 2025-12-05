set -e
set -u

ref_audio=$1
text_path=$2
ref_mp4=$3

pwd=$(pwd)
echo "ref_audio: ${ref_audio}"
echo "text_path: ${text_path}"
echo "ref_mp4: ${ref_mp4}"
echo "pwd: ${pwd}"

real_ref_audio=$(realpath ${ref_audio})
real_text_path=$(realpath ${text_path})
real_ref_mp4=$(realpath ${ref_mp4})

echo "real_ref_audio: ${real_ref_audio}"
echo "real_text_path: ${real_text_path}"
echo "real_ref_mp4: ${real_ref_mp4}"

# tts
cd tts-fish-speech
echo bash run.sh ${real_ref_audio} ${real_text_path}
bash run.sh ${real_ref_audio} ${real_text_path}

# f2f
cd ${pwd}
mv tts-fish-speech/fake.wav example/fake.wav

python run.py --audio_path example/fake.wav --video_path ${ref_mp4}
