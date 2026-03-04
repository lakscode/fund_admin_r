type Environment = 'development' | 'test' | 'production';

interface EnvConfig {
  API_URL: string;
  APP_TITLE: string;
}

const ENV: Environment = (import.meta.env.MODE as Environment) || 'development';

const CONFIG: Record<Environment, EnvConfig> = {
  development: {
    API_URL: 'http://localhost:5000/api',
    APP_TITLE: 'Fund Admin (Dev)',
  },
  test: {
    API_URL: 'http://localhost:5001/api',
    APP_TITLE: 'Fund Admin (Test)',
  },
  production: {
    API_URL: 'https://api.fundadmin.com/api',
    APP_TITLE: 'Fund Admin',
  },
};

const current = CONFIG[ENV] ?? CONFIG.development;

export const API_URL = current.API_URL;
export const APP_TITLE = current.APP_TITLE;
export const IS_DEV = ENV === 'development';
export const IS_TEST = ENV === 'test';
export const IS_PROD = ENV === 'production';
