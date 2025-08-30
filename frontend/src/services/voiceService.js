class VoiceService {
  constructor() {
    this.synthesis = window.speechSynthesis;
    this.voices = [];
    this.currentVoice = null;
    this.rate = 1;
    this.pitch = 1;
    this.volume = 0.8;

    this.loadVoices();
    
    // Handle voices changed event
    if (this.synthesis.onvoiceschanged !== undefined) {
      this.synthesis.onvoiceschanged = () => this.loadVoices();
    }
  }

  loadVoices() {
    this.voices = this.synthesis.getVoices();
    
    // Prefer female voice if available
    const femaleVoice = this.voices.find(voice => 
      voice.name.toLowerCase().includes('female') || 
      voice.name.toLowerCase().includes('zira') ||
      voice.name.toLowerCase().includes('samantha')
    );
    
    this.currentVoice = femaleVoice || this.voices[0] || null;
  }

  speak(text, options = {}) {
    if (!this.synthesis) {
      console.warn('Speech synthesis not supported');
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      // Cancel any ongoing speech
      this.synthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      
      utterance.voice = this.currentVoice;
      utterance.rate = options.rate || this.rate;
      utterance.pitch = options.pitch || this.pitch;
      utterance.volume = options.volume || this.volume;

      utterance.onend = () => resolve();
      utterance.onerror = (event) => reject(event.error);

      this.synthesis.speak(utterance);
    });
  }

  stop() {
    if (this.synthesis) {
      this.synthesis.cancel();
    }
  }

  pause() {
    if (this.synthesis) {
      this.synthesis.pause();
    }
  }

  resume() {
    if (this.synthesis) {
      this.synthesis.resume();
    }
  }

  setVoice(voiceIndex) {
    if (voiceIndex >= 0 && voiceIndex < this.voices.length) {
      this.currentVoice = this.voices[voiceIndex];
    }
  }

  setRate(rate) {
    this.rate = Math.max(0.1, Math.min(10, rate));
  }

  setPitch(pitch) {
    this.pitch = Math.max(0, Math.min(2, pitch));
  }

  setVolume(volume) {
    this.volume = Math.max(0, Math.min(1, volume));
  }

  getVoices() {
    return this.voices.map((voice, index) => ({
      index,
      name: voice.name,
      lang: voice.lang,
      default: voice.default,
      localService: voice.localService
    }));
  }

  isSupported() {
    return 'speechSynthesis' in window;
  }

  isSpeaking() {
    return this.synthesis ? this.synthesis.speaking : false;
  }

  isPaused() {
    return this.synthesis ? this.synthesis.paused : false;
  }

  isPending() {
    return this.synthesis ? this.synthesis.pending : false;
  }
}

export const voiceService = new VoiceService();
