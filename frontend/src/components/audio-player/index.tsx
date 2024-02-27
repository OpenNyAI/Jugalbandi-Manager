import React, { useEffect, useRef, useState } from 'react';

interface props {
    src: string;
    isPlaying: boolean;
    onTogglePlay: () => void;
}


const PlayPauseButton = ({ isPlaying, onClick }:any) => {
    return (
      <button onClick={onClick} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
        {isPlaying ? (
          // Pause icon (two vertical bars)
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
            <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
          </svg>
        ) : (
          // Play icon (right-pointing triangle)
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
            <path d="M8 5v14l11-7z" />
          </svg>
        )}
      </button>
    );
  };
  


const AudioPlayer = ({ src, isPlaying, onTogglePlay }:props) => {
  const audioRef = useRef(new Audio(src));
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);

  // Update the audio player's current time
  const onTimeUpdate = () => {
    setCurrentTime(audioRef.current.currentTime);
  };

  // Set the duration of the audio file once it's loaded
  useEffect(() => {
    const audio = audioRef.current;
    audio.addEventListener('loadedmetadata', () => {
      setDuration(audio.duration);
    });
    audio.addEventListener('timeupdate', onTimeUpdate);

    return () => {
      audio.removeEventListener('loadedmetadata', () => {});
      audio.removeEventListener('timeupdate', onTimeUpdate);
    };
  }, [src]);

  // Play or pause the audio based on isPlaying prop
  useEffect(() => {
    isPlaying ? audioRef.current.play() : audioRef.current.pause();
  }, [isPlaying]);

  const togglePlay = () => {
    onTogglePlay();
  };

  const handleSeek = (e) => {
    const time = (e.target.value / 100) * duration;
    audioRef.current.currentTime = time;
    setCurrentTime(time);
  };

  return (
    <div>
        <PlayPauseButton isPlaying={isPlaying} onClick={onTogglePlay} />
      <input
        type="range"
        value={duration ? (currentTime / duration) * 100 : 0}
        onChange={handleSeek}
      />
    </div>
  );
};

export default AudioPlayer;
