/**
 * TacRaven Solutions - GA4 Enhanced Event Tracking
 * Version: 1.0.0
 * Requires: gtag() must already be loaded on the page
 * 
 * Events tracked:
 * - scroll_depth (25%, 50%, 75%, 100%)
 * - internal_click
 * - outbound_click
 * - cta_click
 * - tool_view
 * - engaged_30s
 * - form_submit
 */

(function() {
    'use strict';

    // Ensure gtag exists before proceeding
    if (typeof gtag !== 'function') {
        console.warn('analytics-events.js: gtag() not found. Events will not fire.');
        return;
    }

    // State tracking to prevent duplicate events
    const state = {
        scrollDepthsFired: new Set(),
        engaged30sFired: false,
        toolViewFired: false
    };

    // Utility: Get current page location
    function getPageLocation() {
        return window.location.href;
    }

    // Utility: Safely get text content, truncated
    function getCleanText(element, maxLength) {
        maxLength = maxLength || 100;
        const text = (element.innerText || element.textContent || '').trim();
        return text.substring(0, maxLength);
    }

    // Utility: Check if URL is internal
    function isInternalLink(url) {
        if (!url) return false;
        try {
            // Relative URLs are internal
            if (url.startsWith('/') || url.startsWith('#') || url.startsWith('./') || url.startsWith('../')) {
                return true;
            }
            // Check if it contains tacraven.com
            if (url.toLowerCase().includes('tacraven.com')) {
                return true;
            }
            // Parse absolute URLs
            const linkHost = new URL(url, window.location.origin).hostname;
            return linkHost === window.location.hostname;
        } catch (e) {
            return false;
        }
    }

    // Utility: Detect tool name from URL
    function detectToolName() {
        const path = window.location.pathname.toLowerCase();
        const toolPatterns = [
            { pattern: /talonprep/i, name: 'talonprep' },
            { pattern: /blackfeather/i, name: 'blackfeather' },
            { pattern: /corvus/i, name: 'corvus' },
            { pattern: /threat-map/i, name: 'threat-map' },
            { pattern: /threatmap/i, name: 'threat-map' }
        ];
        
        for (const tool of toolPatterns) {
            if (tool.pattern.test(path)) {
                return tool.name;
            }
        }
        return null;
    }

    // =========================================
    // 1) SCROLL DEPTH TRACKING
    // =========================================
    function initScrollTracking() {
        const thresholds = [25, 50, 75, 100];
        
        function getScrollPercent() {
            const docHeight = Math.max(
                document.body.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.clientHeight,
                document.documentElement.scrollHeight,
                document.documentElement.offsetHeight
            );
            const windowHeight = window.innerHeight;
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollableHeight = docHeight - windowHeight;
            
            if (scrollableHeight <= 0) return 100;
            return Math.round((scrollTop / scrollableHeight) * 100);
        }

        function checkScrollDepth() {
            const currentPercent = getScrollPercent();
            
            thresholds.forEach(function(threshold) {
                if (currentPercent >= threshold && !state.scrollDepthsFired.has(threshold)) {
                    state.scrollDepthsFired.add(threshold);
                    gtag('event', 'scroll_depth', {
                        percent: threshold,
                        page_location: getPageLocation()
                    });
                }
            });
        }

        // Throttle scroll events
        let scrollTimeout = null;
        window.addEventListener('scroll', function() {
            if (scrollTimeout) return;
            scrollTimeout = setTimeout(function() {
                scrollTimeout = null;
                checkScrollDepth();
            }, 100);
        }, { passive: true });

        // Check initial scroll position
        checkScrollDepth();
    }

    // =========================================
    // 2) INTERNAL LINK CLICK TRACKING
    // =========================================
    function initInternalLinkTracking() {
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a');
            if (!link) return;
            
            const href = link.getAttribute('href');
            if (!href || href === '#') return;
            
            // Skip if it has cta-button class (handled separately)
            if (link.classList.contains('cta-button')) return;
            
            if (isInternalLink(href)) {
                gtag('event', 'internal_click', {
                    link_text: getCleanText(link),
                    link_url: href,
                    page_location: getPageLocation()
                });
            }
        }, { passive: true });
    }

    // =========================================
    // 3) OUTBOUND LINK TRACKING
    // =========================================
    function initOutboundLinkTracking() {
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a');
            if (!link) return;
            
            const href = link.getAttribute('href');
            if (!href || href.startsWith('#') || href.startsWith('javascript:')) return;
            
            // Only track if it's NOT internal (i.e., it's outbound)
            if (!isInternalLink(href)) {
                gtag('event', 'outbound_click', {
                    link_url: href,
                    page_location: getPageLocation()
                });
            }
        }, { passive: true });
    }

    // =========================================
    // 4) CTA BUTTON TRACKING
    // =========================================
    function initCtaTracking() {
        document.addEventListener('click', function(e) {
            const ctaButton = e.target.closest('.cta-button');
            if (!ctaButton) return;
            
            gtag('event', 'cta_click', {
                cta_text: getCleanText(ctaButton),
                page_location: getPageLocation()
            });
        }, { passive: true });
    }

    // =========================================
    // 5) TOOL VIEW TRACKING
    // =========================================
    function initToolViewTracking() {
        if (state.toolViewFired) return;
        
        const toolName = detectToolName();
        if (toolName) {
            state.toolViewFired = true;
            gtag('event', 'tool_view', {
                tool_name: toolName
            });
        }
    }

    // =========================================
    // 6) ENGAGEMENT TIMER (30 SECONDS)
    // =========================================
    function initEngagementTimer() {
        setTimeout(function() {
            if (state.engaged30sFired) return;
            state.engaged30sFired = true;
            gtag('event', 'engaged_30s', {
                page_location: getPageLocation()
            });
        }, 30000);
    }

    // =========================================
    // 7) FORM SUBMISSION TRACKING
    // =========================================
    function initFormTracking() {
        document.addEventListener('submit', function(e) {
            const form = e.target;
            if (!form || form.tagName !== 'FORM') return;
            
            const formName = form.getAttribute('name') 
                || form.getAttribute('id') 
                || form.getAttribute('data-form-name')
                || 'unnamed_form';
            
            gtag('event', 'form_submit', {
                form_name: formName,
                page_location: getPageLocation()
            });
        }, { passive: true });
    }

    // =========================================
    // INITIALIZE ALL TRACKING
    // =========================================
    function init() {
        try {
            initScrollTracking();
            initInternalLinkTracking();
            initOutboundLinkTracking();
            initCtaTracking();
            initToolViewTracking();
            initEngagementTimer();
            initFormTracking();
        } catch (err) {
            console.error('analytics-events.js initialization error:', err);
        }
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
