import { NextFunction, Response, ErrorRequestHandler } from 'express';
import { logger } from '../logger/logger';
import { Request } from '../types/request';
import { ResultCode } from '../types/result_code';
import { ApiResult } from '../types/api_result';
import { config } from '../../config';

export const exceptionMiddlewares: ErrorRequestHandler = async (err: Error, req: Request, res: Response, next: NextFunction) => {
    const result: ApiResult = {
        code: ResultCode.Fail,
        message: ResultCode[ResultCode.Fail],
    };

    if (['dev', 'local'].includes(config.nodeEnv)) {
        result.message = err.message;
    }

    logger.error({
        name: err.name,
        message: err.message,
        stack: err.stack,
        url: req.url,
        headers: req.headers,
    });
    
    res.json(result);
};