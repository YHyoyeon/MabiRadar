import { NextFunction, Response, RequestHandler } from 'express';
import { Request } from '../../shared/types/request';
import { ApiResult } from '../../shared/types/api_result';
import { ResultCode } from '../../shared/types/result_code';
import { Meta } from '../../shared/types/meta';

/**
 * @openapi
 * /api/health:
 *   get:
 *     tags:
 *       - health
 *     summary: health!
 *     responses:
 *       '200':
 *         description: Successful operation
 */

export const execute: RequestHandler = async (req: Request, res: Response, next: NextFunction) => {
    const result: ApiResult = {
        code: 1,
        message: ResultCode[ResultCode.Success],
    };

    req.response = result;
    return next();
};

export const meta: Meta = {
    method: 'get',
    enable: true,
};