import fs from 'fs';
import os from 'os';
import winston from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';

export abstract class WinstonLogger {
    _logger: winston.Logger;

    _host = os.hostname();

    _customLevels: winston.config.AbstractConfigSetLevels = {
        error: 0, // 예외나 치명적인 오류
        warn: 1, // 경고 메시지를 나타내며, 프로그램이 정상 작동하지만 주의가 필요한 상황
        info: 2, // 일반적인 정보성 메시지 (서버 시작, 요청 수신 등)
        http: 3, // http 통신
        verbose: 4, // sql
        debug: 5, // 디버깅 목적으로 세부 정보를 기록 * 프로덕션 환경에서 비활성화 (특정 함수나 모듈 내부의 변수 값, 흐름 제어)
        silly: 6, // 매우 낮은 중요도와 상세 정보 (디버깅 목적)
    };

    _fileFormat = winston.format.combine(
        winston.format.timestamp({ format: 'YYYY-MM-DDTHH:mm:ss.SSSZ' }),
        winston.format.json(),
    );

    _consoleFormat = {
        format: winston.format.combine(
            winston.format.colorize(),
            winston.format.timestamp({ format: 'YYYY-MM-DDTHH:mm:ss.SSSZ' }),
            winston.format.printf(({ level, message, timestamp }) => {
                return `${timestamp} [${level}]: ${message}`;
            }),
        ),
        level: 'silly'
    };

    constructor(directoryPath: string, name: string, logLevel?: string, enableConsole = true) {
        this.checkDirectory(directoryPath); // 로그 디렉토리 체크 및 생성
        const rotateFile = new DailyRotateFile({
            dirname: directoryPath,
            filename: `${name}_%DATE%.log`,
            datePattern: 'YYYYMMDD',
            // 특정 수준 이상의 로그만을 기록
            level: logLevel ?? 'silly',
            // 보관할 최대 로그 수. 파일 수 또는 일수(일: 접미사로 'd' 추가) (기본값: null)
            maxFiles: '10d',
        });
        this._logger = this.setLogger(rotateFile, enableConsole);
    }

    get logger(): winston.Logger {
        return this._logger;
    }

    emit(eventName: string, msg: string) {
        // 추상 메서드로 구현 클래스에서 사용자가 정의하도록 설정
    }

    setLogger(rotateFile: DailyRotateFile, enableConsole: boolean) {
        const logger = winston.createLogger({
            levels: this._customLevels,
            format: this._fileFormat,
            transports: [rotateFile],
        });

        if (enableConsole) {
            logger.add(new winston.transports.Console(
                this._consoleFormat
            ));
        }

        const originalError: winston.LeveledLogMethod = logger.error.bind(logger);

        // error 함수 오버라이드
        logger.error = (message: any, ...args: any[]): winston.Logger => {
            const buildMessage = (...args: any[]) => {
                return args.map(arg => {
                    try {
                        return JSON.stringify(arg); // JSON 직렬화
                    }
                    catch {
                        return String(arg); // 직렬화 실패 시 문자열 변환
                    }
                }).join(' ');
            };

            this.emit('error', `${message} ${args.length ? buildMessage(args) : ''}`); // 'error' 이벤트 발생

            originalError(message, ...args);
            return logger;
        };

        return logger;
    }

    mkdir(path: string, root?: string) {
        const dirs = path.split('/');
        const dir = dirs.shift();
        const targetRoot = (root || '') + dir + '/';

        try {
            fs.mkdirSync(targetRoot);
        }
        catch (error) {
            if (!fs.statSync(targetRoot).isDirectory())
                throw new Error(error as any); // 디렉터리가 아닌 경우 오류 발생
        }

        return !dirs.length || this.mkdir(dirs.join('/'), targetRoot);
    }

    checkDirectory(directoryPath: string) {
        try {
            const stats = fs.lstatSync(directoryPath);

            if (stats.isDirectory()) {
                return; // 디렉터리가 이미 존재하면 종료
            }
        }
        catch {
            this.mkdir(directoryPath); // 디렉터리 생성
        }
    }
}
