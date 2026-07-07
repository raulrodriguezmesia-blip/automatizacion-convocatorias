import axios, { AxiosInstance } from 'axios';

export interface TenantConfig {
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
}

export interface Convocatoria {
  id: string;
  title: string;
  startDatetime: string;
  attendees: string[];
  location?: string;
  description?: string;
}

export interface BusinessMetrics {
  tenantId: string;
  convocatoriasMes: number;
  horasAhorradas: number;
  participacionPromedio: number;
  nps?: number;
  apiCallsTotal: number;
  modelAccuracy: number;
}

export class ConvocatoriaClient {
  private client: AxiosInstance;
  private config: TenantConfig;

  constructor(config: TenantConfig) {
    this.config = { ...config, baseUrl: config.baseUrl || 'https://api.convocatorias.io/v1' };
    this.client = axios.create({
      baseURL: this.config.baseUrl,
      timeout: config.timeout || 30000,
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'Content-Type': 'application/json',
        'User-Agent': '@convocatorias/sdk/1.0.0',
      },
    });
  }

  async createConvocatoria(params: {
    title: string;
    startDatetime: string;
    attendees: string[];
    location?: string;
    description?: string;
  }): Promise<Convocatoria> {
    const response = await this.client.post('/convocatorias', params);
    return response.data;
  }

  async listConvocatorias(limit = 50): Promise<Convocatoria[]> {
    const response = await this.client.get(`/convocatorias?limit=${limit}`);
    return response.data;
  }

  async processDocument(filePath: string, useLlm = false): Promise<any> {
    const FormData = require('form-data');
    const fs = require('fs');
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    form.append('use_llm', String(useLlm));
    
    const response = await axios.post(
      `${this.config.baseUrl}/documents/process`,
      form,
      {
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`,
          ...form.getHeaders(),
        },
      }
    );
    return response.data;
  }

  async getTemplates(category?: string): Promise<any[]> {
    const response = await this.client.get(
      `/templates${category ? `?category=${category}` : ''}`
    );
    return response.data;
  }

  async getTenantMetrics(): Promise<BusinessMetrics> {
    const response = await this.client.get('/tenant/metrics');
    return response.data;
  }
}

export function getVersion(): string {
  return '1.0.0-beta';
}