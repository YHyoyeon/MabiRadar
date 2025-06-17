import { NextFunction, Response, RequestHandler } from 'express';
import { Request } from '../../shared/types/request';

export const responseMiddleware: RequestHandler = async (req: Request, res: Response, next: NextFunction) => {
    if (res.statusCode !== 200) {
        res.json();
        return;
    }

    res.status(200).json(req.response);
    return;
};