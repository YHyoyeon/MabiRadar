import swaggerJsdoc from 'swagger-jsdoc';
import { config } from './config';

const swaggerOptions = {
    definition: {
        openapi: '3.0.0',
        info: {
            title: 'Radar API',
            version: '1.0.0',
            description: 'Radar API',
        },
        servers: [
            {
                url: `http://localhost:${config.radarServer.port}`,
            },
        ],
    },
    apis: ['./src/app_radar/controllers/**/*.ts', './src/app_radar/controllers/**/*.js'],
};

export const swaggerDocs = swaggerJsdoc(swaggerOptions);
