import express, { RequestHandler } from 'express';
import fs from 'fs';
import path from 'path';
import { logger } from '../../shared/logger/logger';
import * as middlewares from '../../shared/middlewares/index';
import { Meta } from '../../shared/types/meta';

const controllersPath = path.resolve(__dirname, '../controllers');

function getControllerFiles(dirPath: string): string[] {
    const results: string[] = [];
    const files = fs.readdirSync(dirPath);

    for (let i = 0; i < files.length; i++) {
        const filePath = path.join(dirPath, files[i]);
        const stat = fs.statSync(filePath);

        if (stat.isDirectory()) {
            results.push(...getControllerFiles(filePath));
        }
        else if (files[i].endsWith('_controller.ts')) {
            results.push(filePath);
        }
    }

    return results;
}

export default async function (router: express.Router) {
    const controllerFiles = getControllerFiles(controllersPath);
    const registeredRoutes = new Set<string>();

    logger.info('🔍 발견된 컨트롤러 파일:', controllerFiles);

    for (let i = 0; i < controllerFiles.length; i++) {
        const filePath = controllerFiles[i];
        const controller = await import(filePath);

        const execute: RequestHandler = controller.execute;
        const meta: Meta = controller.meta;

        if (typeof execute !== 'function' || !meta) {
            logger.warn(`⚠️ ${filePath}에서 'execute' 함수 또는 'meta' 정보가 없습니다.`);
            continue;
        }

        const relativePath = path.relative(controllersPath, filePath);
        const routePath = '/' + relativePath.replace('_controller.ts', '').replace(/\\/g, '/');
        const method = meta.method || 'get';

        if (registeredRoutes.has(routePath)) {
            logger.warn(`⚠️ 중복된 라우트 발견: ${routePath}`);
            continue;
        }

        registeredRoutes.add(routePath);

        router[method](
            routePath,
            [
                execute,
                middlewares.responseMiddleware,
            ].filter(Boolean)
        );

        logger.info(`✅ 라우트 등록 완료: [${method.toUpperCase()}] ${routePath}`);
    }
}
