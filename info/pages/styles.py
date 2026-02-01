"""
Estilos compartidos - Glassmorphism elegante estilo Apple
"""

BASE_STYLES = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    :root {
        --primary: #FF6B9D;
        --primary-light: #FFB4D0;
        --primary-dark: #E84A7F;
        --bg-start: #1a1a2e;
        --bg-mid: #16213e;
        --bg-end: #0f0f23;
        --glass-bg: rgba(255, 255, 255, 0.08);
        --glass-border: rgba(255, 255, 255, 0.15);
        --glass-shadow: rgba(0, 0, 0, 0.3);
        --text-primary: #ffffff;
        --text-secondary: rgba(255, 255, 255, 0.7);
        --text-muted: rgba(255, 255, 255, 0.5);
        --success: #34D399;
        --error: #F87171;
    }
    
    html {
        font-size: 16px;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    body {
        min-height: 100vh;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: linear-gradient(135deg, var(--bg-start) 0%, var(--bg-mid) 50%, var(--bg-end) 100%);
        color: var(--text-primary);
        line-height: 1.6;
        overflow-x: hidden;
    }
    
    /* Fondo animado sutil */
    body::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(ellipse at 20% 20%, rgba(255, 107, 157, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
        pointer-events: none;
        z-index: -1;
    }
    
    /* Contenedor principal */
    .container {
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 24px;
    }
    
    /* Tarjeta Glass */
    .glass-card {
        width: 100%;
        max-width: 480px;
        background: var(--glass-bg);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        padding: 40px 32px;
        box-shadow: 
            0 8px 32px var(--glass-shadow),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .glass-card.large {
        max-width: 640px;
        padding: 48px 40px;
    }
    
    /* Avatar */
    .avatar-container {
        display: flex;
        justify-content: center;
        margin-bottom: 24px;
    }
    
    .avatar {
        width: 88px;
        height: 88px;
        border-radius: 50%;
        border: 3px solid var(--glass-border);
        box-shadow: 0 8px 24px rgba(255, 107, 157, 0.3);
        object-fit: cover;
    }
    
    .avatar-placeholder {
        width: 88px;
        height: 88px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
    }
    
    /* Iconos grandes */
    .icon-large {
        font-size: 3.5rem;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Tipografía */
    h1 {
        font-size: 1.75rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 8px;
        background: linear-gradient(135deg, #fff 0%, var(--primary-light) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h2 {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 28px 0 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    h2 .icon {
        font-size: 1.1rem;
    }
    
    .subtitle {
        text-align: center;
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin-bottom: 28px;
    }
    
    p {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin-bottom: 16px;
    }
    
    ul {
        list-style: none;
        padding: 0;
    }
    
    li {
        color: var(--text-secondary);
        font-size: 0.9rem;
        padding: 8px 0;
        padding-left: 24px;
        position: relative;
    }
    
    li::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--primary);
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: rgba(52, 211, 153, 0.15);
        border: 1px solid rgba(52, 211, 153, 0.3);
        padding: 12px 24px;
        border-radius: 100px;
        margin: 20px auto;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background: var(--success);
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
    }
    
    .status-text {
        color: var(--success);
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Botones */
    .btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 14px 28px;
        border-radius: 12px;
        font-size: 0.95rem;
        font-weight: 600;
        text-decoration: none;
        border: none;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: #fff;
        box-shadow: 0 4px 16px rgba(255, 107, 157, 0.4);
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(255, 107, 157, 0.5);
    }
    
    .btn-secondary {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        color: var(--text-primary);
    }
    
    .btn-secondary:hover {
        background: rgba(255, 255, 255, 0.12);
    }
    
    .btn-group {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-top: 24px;
    }
    
    /* Info Box */
    .info-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 20px;
        margin: 20px 0;
    }
    
    .info-box.success {
        background: rgba(52, 211, 153, 0.1);
        border-color: rgba(52, 211, 153, 0.2);
    }
    
    .info-box.error {
        background: rgba(248, 113, 113, 0.1);
        border-color: rgba(248, 113, 113, 0.2);
    }
    
    /* Features Grid */
    .features {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        margin: 24px 0;
    }
    
    .feature-item {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 20px 16px;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .feature-item:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateY(-2px);
    }
    
    .feature-icon {
        font-size: 1.75rem;
        margin-bottom: 8px;
        display: block;
    }
    
    .feature-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 4px;
    }
    
    .feature-desc {
        font-size: 0.75rem;
        color: var(--text-muted);
    }
    
    /* Code Box */
    .code-box {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 16px 20px;
        font-family: 'SF Mono', 'Fira Code', monospace;
        font-size: 0.85rem;
        color: var(--primary-light);
        text-align: center;
        margin: 16px 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 32px;
        padding-top: 20px;
        border-top: 1px solid var(--glass-border);
        color: var(--text-muted);
        font-size: 0.8rem;
    }
    
    /* Links */
    a {
        color: var(--primary-light);
        text-decoration: none;
        transition: color 0.2s;
    }
    
    a:hover {
        color: var(--primary);
    }
    
    /* Animaciones */
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.1); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .glass-card {
        animation: fadeIn 0.4s ease-out;
    }
    
    /* Responsive */
    @media (max-width: 480px) {
        .glass-card {
            padding: 32px 24px;
            border-radius: 20px;
        }
        
        .glass-card.large {
            padding: 32px 24px;
        }
        
        h1 {
            font-size: 1.5rem;
        }
        
        .features {
            grid-template-columns: 1fr;
        }
        
        .btn {
            width: 100%;
        }
    }
</style>
"""

META_TAGS = """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#1a1a2e">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
"""
