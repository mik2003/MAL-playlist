// PWA Manager - Handles installation and service worker
class PWAManager {
    constructor() {
        this.deferredPrompt = null;
        this.init();
    }

    init() {
        this.checkPWAStatus();
        if (this.isServiceWorkerSupported()) {
            this.registerServiceWorker();
        } else {
            this.fallbackPWA();
        }
        this.setupInstallPrompt();
    }

    isServiceWorkerSupported() {
        return 'serviceWorker' in navigator &&
            (window.location.protocol === 'https:' ||
                window.location.hostname === 'localhost' ||
                window.location.hostname === '127.0.0.1');
    }

    registerServiceWorker() {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('./sw.js')
                .then(reg => {
                    console.log('✅ Service Worker registered:', reg.scope);
                    this.showInstallButton();
                })
                .catch(err => {
                    console.log('❌ Service Worker failed:', err);
                    this.fallbackPWA();
                });
        });
    }

    fallbackPWA() {
        console.log('⚠️ Using fallback PWA without Service Worker');
        // We can still try to make it installable without SW
        this.showInstallButton();

        // Check if we can still trigger install prompt
        setTimeout(() => {
            if (!this.deferredPrompt) {
                console.log('No install prompt received - may need HTTPS');
            }
        }, 3000);
    }

    setupInstallPrompt() {
        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('✅ BEFORE INSTALL PROMPT FIRED');
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        });

        if (window.matchMedia('(display-mode: standalone)').matches) {
            console.log('✅ Running as installed PWA');
        }
    }

    showInstallButton() {
        const installBtn = document.getElementById('install-btn');
        if (installBtn) {
            installBtn.style.display = 'inline-block';
            installBtn.onclick = () => this.installApp();
        }
    }

    installApp() {
        if (this.deferredPrompt) {
            this.deferredPrompt.prompt();
            this.deferredPrompt.userChoice.then((choiceResult) => {
                console.log('Installation:', choiceResult.outcome);
                this.deferredPrompt = null;
                const installBtn = document.getElementById('install-btn');
                if (installBtn) installBtn.style.display = 'none';
            });
        } else {
            alert('PWA installation not available. Try visiting with HTTPS or localhost.');
        }
    }

    checkPWAStatus() {
        console.log('=== PWA Status Check ===');
        console.log('- HTTPS:', window.location.protocol === 'https:');
        console.log('- SW supported:', this.isServiceWorkerSupported());
        console.log('- Hostname:', window.location.hostname);
        console.log('- Manifest:', !!document.querySelector('link[rel="manifest"]'));
    }
}

// Initialize PWA Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PWAManager();
});