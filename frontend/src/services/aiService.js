import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

class AIService {
  constructor() {
    this.axios = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for logging
    this.axios.interceptors.request.use(
      (config) => {
        console.log('API Request:', config.method.toUpperCase(), config.url);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.axios.interceptors.response.use(
      (response) => {
        console.log('API Response:', response.status, response.config.url);
        return response;
      },
      (error) => {
        console.error('API Response Error:', error.response || error.message);
        return Promise.reject(error);
      }
    );
  }

  async sendMessage(data) {
    try {
      const response = await this.axios.post('/chat', data);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to send message: ${error.response?.data?.detail || error.message}`);
    }
  }

  async uploadFile(file, onProgress = null) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await this.axios.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: onProgress ? (progressEvent) => {
          const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentage);
        } : undefined,
      });

      return response.data;
    } catch (error) {
      throw new Error(`Failed to upload file: ${error.response?.data?.detail || error.message}`);
    }
  }

  async searchWeb(query, numResults = 3) {
    try {
      const response = await this.axios.post(`/web/search?query=${encodeURIComponent(query)}&num_results=${numResults}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to search web: ${error.response?.data?.detail || error.message}`);
    }
  }

  async scrapeUrl(url, options = {}) {
    try {
      const response = await this.axios.post('/web/scrape', {
        url,
        extract_links: options.extractLinks || false,
        extract_images: options.extractImages || false,
        max_pages: options.maxPages || 1,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to scrape URL: ${error.response?.data?.detail || error.message}`);
    }
  }

  async textToSpeech(text, options = {}) {
    try {
      const response = await this.axios.post('/voice/tts', {
        text,
        voice: options.voice || 'default',
        speed: options.speed || 150,
        output_format: options.format || 'mp3',
      }, {
        responseType: 'blob',
      });

      return response.data;
    } catch (error) {
      throw new Error(`Failed to convert text to speech: ${error.response?.data?.detail || error.message}`);
    }
  }

  async speechToText(audioBlob) {
    try {
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'audio.wav');

      const response = await this.axios.post('/voice/stt', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      throw new Error(`Failed to convert speech to text: ${error.response?.data?.detail || error.message}`);
    }
  }

  async calculate(expression) {
    try {
      const response = await this.axios.post(`/task/calculate?expression=${encodeURIComponent(expression)}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to calculate: ${error.response?.data?.detail || error.message}`);
    }
  }

  async getVoices() {
    try {
      const response = await this.axios.get('/voice/voices');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get voices: ${error.response?.data?.detail || error.message}`);
    }
  }

  async getKnowledgeSummary() {
    try {
      const response = await this.axios.get('/knowledge/summary');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get knowledge summary: ${error.response?.data?.detail || error.message}`);
    }
  }

  async getStats() {
    try {
      const response = await this.axios.get('/stats');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get stats: ${error.response?.data?.detail || error.message}`);
    }
  }

  async getHealth() {
    try {
      const response = await this.axios.get('/health');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get health status: ${error.response?.data?.detail || error.message}`);
    }
  }

  async createAutomationTask(taskType, parameters, schedule = null) {
    try {
      const response = await this.axios.post('/tasks/automate', {
        task_type: taskType,
        parameters,
        schedule,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to create automation task: ${error.response?.data?.detail || error.message}`);
    }
  }
}

export const aiService = new AIService();
