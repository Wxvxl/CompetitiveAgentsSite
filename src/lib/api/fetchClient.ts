// 定义通用响应类型
interface ApiResponse<T = any> {
    code: number;
    data: T;
    message: string;
  }
  
  // 请求配置类型
  interface RequestOptions extends RequestInit {
    params?: Record<string, any>;
  }
  
  // 基础URL
  const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '/api';
  
  // 处理URL参数
  const resolveUrl = (url: string, params?: Record<string, any>) => {
    if (!params) return url;
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) searchParams.append(key, String(value));
    });
    return `${url}?${searchParams.toString()}`;
  };
  
  // 请求拦截处理
  const handleRequest = (url: string, options: RequestOptions = {}) => {
    // 拼接完整URL
    const fullUrl = url.startsWith('http') ? url : `${BASE_URL}${url}`;
    const resolvedUrl = resolveUrl(fullUrl, options.params);
    
    // 默认配置
    const defaultOptions: RequestOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      method: options.method || 'GET',
    };
    
    // 添加认证token
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : '';
    if (token) {
      defaultOptions.headers = {
        ...defaultOptions.headers,
        Authorization: `Bearer ${token}`,
      };
    }
    
    // 处理请求体
    if (options.body && typeof options.body === 'object') {
      defaultOptions.body = JSON.stringify(options.body);
    }
    
    return { url: resolvedUrl, options: defaultOptions };
  };
  
  // 响应拦截处理
  const handleResponse = async <T>(response: Response): Promise<T> => {
    if (!response.ok) {
      // 处理HTTP错误状态码
      if (response.status === 401) {
        // 未授权，跳转到登录页（仅客户端）
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        throw new Error('登录已过期，请重新登录');
      }
      
      throw new Error(`请求失败: ${response.status} ${response.statusText}`);
    }
    
    // 解析JSON响应
    const data: ApiResponse<T> = await response.json();
    
    // 处理业务错误码
    if (data.code !== 200) {
      throw new Error(data.message || '接口返回错误');
    }
    
    return data.data;
  };
  
  // 封装请求方法
  export const request = {
    get: async <T>(url: string, options?: RequestOptions) => {
      const { url: resolvedUrl, options: requestOptions } = handleRequest(url, {
        ...options,
        method: 'GET',
      });
      const response = await fetch(resolvedUrl, requestOptions);
      return handleResponse<T>(response);
    },
    
    post: async <T>(url: string, data?: any, options?: RequestOptions) => {
      const { url: resolvedUrl, options: requestOptions } = handleRequest(url, {
        ...options,
        method: 'POST',
        body: data,
      });
      const response = await fetch(resolvedUrl, requestOptions);
      return handleResponse<T>(response);
    },
    
    // 可继续添加put、delete等方法
  };
  
  export default request;
      