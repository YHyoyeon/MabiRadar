import express from 'express';
import { ApiResult } from './api_result';

export interface Request extends express.Request {
    response: ApiResult;
}