import path from 'path';
import { WinstonLogger } from './winston_logger';
import EventEmitter from 'events';
import { config } from '../../config';

const name = config.radarServer.name;
const logPath = path.join('./log/', name); // 로그 디렉터리 설정
const channel = new EventEmitter(); // 이벤트 채널 생성

class Logger extends WinstonLogger {
    constructor(directoryPath: string, name: string, logLevel?: string, enableConsole = true) {
        super(directoryPath, name, logLevel, enableConsole); // 부모 클래스 초기화
    }

    emit(eventName: string, msg: string) {
        if (channel.listenerCount('error') > 0) {
            channel.emit('error', msg); // 'error' 이벤트 발생
        }
    }

    addListener(event: string, listener: (...args: any[]) => void) {
        channel.addListener(event, listener); // 이벤트 리스너 추가
    }

    removeListener(event: string, listener: (...args: any[]) => void) {
        channel.removeListener(event, listener); // 이벤트 리스너 제거
    }
}

export const logger = new Logger(logPath, name).logger; // Logger 인스턴스 생성 및 내보내기
