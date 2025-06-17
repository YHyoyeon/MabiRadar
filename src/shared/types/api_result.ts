export interface ApiResult {
    code: number;
    message?: string;
    [key: string]: any;
}