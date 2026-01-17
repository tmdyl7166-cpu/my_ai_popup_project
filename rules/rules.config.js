/**
 * AI弹窗项目 - 规则配置文件
 * 
 * 本配置文件定义了规则系统的全局配置和约束
 */

// =======================
// 基础配置
// =======================
const config = {
    // 项目基本信息
    project: {
        name: "AI弹窗项目 - 智能人脸合成与视频处理平台",
        version: "1.0.0",
        code: "my_ai_popup_project"
    },
    
    // 规则系统配置
    rules: {
        // 配置层级顺序（不可更改）
        layerOrder: ['L1', 'L2', 'L3', 'L4', 'L5'],
        
        // 配置文件路径模板
        layerPathTemplate: './{layer}.json',
        
        // 是否启用配置验证
        validationEnabled: true,
        
        // 配置热重载（开发模式）
        hotReload: false
    },
    
    // 性能配置
    performance: {
        // 最大并行任务数
        maxConcurrentTasks: 4,
        
        // 任务超时时间（毫秒）
        taskTimeout: 300000,
        
        // 缓存策略
        cache: {
            enabled: true,
            maxAge: 3600, // 秒
            maxSize: 1000 // 条目
        }
    },
    
    // 日志配置
    logging: {
        level: 'INFO',
        format: 'json',
        output: ['console', 'file'],
        filePath: './logs/rules.log'
    },
    
    // 兼容性配置
    compatibility: {
        python: {
            minVersion: '3.10',
            maxVersion: '3.11'
        },
        node: {
            minVersion: '18.0.0'
        }
    },
    
    // 特征开关
    features: {
        realtimeProcessing: true,
        batchProcessing: true,
        aiCommandUnderstanding: true,
        virtualCamera: true,
        obsIntegration: true,
        performanceMonitoring: true
    },
    
    // 安全配置
    security: {
        // 是否启用认证
        authentication: false,
        // 是否启用速率限制
        rateLimiting: true,
        // 最大请求频率（每分钟）
        maxRequestsPerMinute: 60
    },
    
    // AI引擎配置
    ai: {
        ollama: {
            host: 'http://localhost:11434',
            defaultModel: 'llama3.2:3b',
            timeout: 300000
        },
        faceRecognition: {
            defaultEngine: 'insightface',
            fallbackEngine: 'dlib'
        }
    },
    
    // 视频处理配置
    video: {
        // 支持的格式
        supportedFormats: ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
        // 最大文件大小（字节）
        maxFileSize: 5 * 1024 * 1024 * 1024, // 5GB
        // 默认帧率
        defaultFps: 30,
        // 最大分辨率
        maxResolution: {
            width: 3840,
            height: 2160
        }
    },
    
    // 图片处理配置
    image: {
        supportedFormats: ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff'],
        maxFileSize: 100 * 1024 * 1024, // 100MB
        maxResolution: {
            width: 8192,
            height: 8192
        }
    },
    
    // 任务状态配置
    taskStates: [
        'pending',           // 待处理
        'resource_loading',  // 资源加载中
        'ai_processing',     // AI处理中
        'synthesizing',      // 合成中
        'output_generating', // 输出生成中
        'completed',         // 已完成
        'failed',            // 失败
        'cancelled'          // 已取消
    ],
    
    // 任务类型配置
    taskTypes: {
        'image_to_camera': {
            name: '图片合成到实时摄像头',
            engines: ['deep-live-cam', 'facefusion'],
            priority: 1
        },
        'image_to_video': {
            name: '图片合成到视频',
            engines: ['deep-live-cam', 'iroop', 'moviepy'],
            priority: 2
        },
        'video_to_camera': {
            name: '视频呈现到实时摄像头',
            engines: ['obs', 'virtual-camera'],
            priority: 1
        },
        'image_to_image': {
            name: '图片合成到图片',
            engines: ['facefusion', 'opencv'],
            priority: 3
        },
        'ai_analyze': {
            name: 'AI分析与理解',
            engines: ['ollama'],
            priority: 4
        },
        'ai_create': {
            name: 'AI创造新内容',
            engines: ['ollama', 'stable-diffusion'],
            priority: 5
        }
    },
    
    // 进度报告配置
    progressReporting: {
        // 报告间隔（毫秒）
        reportInterval: 100,
        // 详细程度：'brief', 'normal', 'detailed'
        detailLevel: 'normal'
    }
};

module.exports = config;

