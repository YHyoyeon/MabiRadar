import { NextFunction, Response, RequestHandler } from 'express';
import { Request } from '../../shared/types/request';

import { logger } from '../logger/logger';

export const notfoundMiddleware: RequestHandler = async (req: Request, res: Response, next: NextFunction) => {
    logger.warn('notfound', {
        method: req.method,
        url: req.url,
        headers: req.headers,
        body: req.body,
    });

    res.status(404).json();
    return;
};