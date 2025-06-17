import express from 'express';
import compression from 'compression';
import cors from 'cors';
import { config } from '../../config';
import dynamicRouteLoader from '../routes/route_generator';
import * as middlewares from '../../shared/middlewares/index';
import swaggerUi from 'swagger-ui-express';
import { swaggerDocs } from '../../swagger_doc';

export async function init(app: express.Express) {
    app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocs));

    const corsOptions = {
        origin: config.nodeEnv,
        allowedHeaders: [
            'content-type',
            'authorization',
            'idempotency-key',
            'refresh',
            'language',
        ],
    };

    app.use(cors(corsOptions));
    app.use(express.json({ limit: '1mb' }));
    app.use(express.urlencoded({ extended: true }));
    app.use(compression());

    const router = express.Router();
    await dynamicRouteLoader(router);

    app.use('/api', router);
    app.use(middlewares.notfoundMiddleware);
    app.use(middlewares.exceptionMiddlewares);
}