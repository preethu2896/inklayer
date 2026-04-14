/* ═══════════════════════════════════════════════════════════════
   INKLAYER — MAIN.JS
   Complete JavaScript Architecture
   ═══════════════════════════════════════════════════════════════ */

import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';
import { initMetallicLogo } from './metallicPaint.js';

gsap.registerPlugin(ScrollTrigger);

/* ───────────────────────────────────────────────────────────────
   LENIS SMOOTH SCROLL
   ─────────────────────────────────────────────────────────────── */
const lenis = new Lenis({
  lerp: 0.1,
  wheelMultiplier: 1,
  infinite: false,
  gestureOrientation: 'vertical',
  normalizeWheel: true,
  smoothWheel: true,
});

lenis.on('scroll', ScrollTrigger.update);

gsap.ticker.add((time) => {
  lenis.raf(time * 1000);
});

gsap.ticker.lagSmoothing(0);

// Add smooth scrolling to all anchor links (including Inklayer logo)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const targetId = this.getAttribute('href');
    const scrollOptions = {
      duration: 1.5,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t))
    };
    if (targetId === '#hero' || targetId === '#') {
      lenis.scrollTo(0, scrollOptions);
    } else {
      const targetEl = document.querySelector(targetId);
      if (targetEl) {
        lenis.scrollTo(targetEl, scrollOptions);
      }
    }
  });
});

/* ───────────────────────────────────────────────────────────────
   HERO ANIMATIONS
   ─────────────────────────────────────────────────────────────── */
function initHeroAnimations() {
  const bgVideo = document.querySelector('.bg-video');
  const heroTitle = document.querySelector('.hero-title');
  const heroSubtitle = document.querySelector('.hero-subtitle');
  const heroCta = document.querySelector('.hero-cta-group');
  const heroDetails = document.querySelector('.hero-details');
  const nav = document.querySelector('.nav');

  if (!bgVideo) return;

  // Entrance Timeline
  // Force video to play immediately if supported
  bgVideo.play().catch(() => {});

  const heroTl = gsap.timeline({ defaults: { ease: 'power2.out' } });

  gsap.set(bgVideo, { scale: 1.2, opacity: 1 });
  gsap.set(heroTitle, { y: 60, opacity: 0 });
  gsap.set(heroSubtitle, { y: 40, opacity: 0 });
  gsap.set(heroCta, { y: 30, opacity: 0 });
  gsap.set(nav, { y: -100, opacity: 0 });

  heroTl
    .to(bgVideo, { scale: 1.05, duration: 2.5 })
    .to(heroTitle, { y: 0, opacity: 1, duration: 1.2 }, '-=2.0')
    .to(heroSubtitle, { y: 0, opacity: 1, duration: 1 }, '-=0.8')
    .to(heroCta, { y: 0, opacity: 1, duration: 1 }, '-=0.6')
    .to(nav, { y: 0, opacity: 1, duration: 1, ease: 'power4.out' }, '-=0.8');

  // Scroll-driven parallax
  gsap.to(bgVideo, {
    scale: 1,
    scrollTrigger: {
      trigger: '.hero',
      start: 'top top',
      end: 'bottom top',
      scrub: true,
    },
  });

  gsap.to(heroDetails, {
    y: -150,
    scrollTrigger: {
      trigger: '.hero',
      start: 'top top',
      end: 'bottom top',
      scrub: true,
    },
  });


}

/* ───────────────────────────────────────────────────────────────
   NAVIGATION SCROLL BEHAVIOR
   ─────────────────────────────────────────────────────────────── */
function initNavScroll() {
  const nav = document.querySelector('.nav');
  const hero = document.querySelector('.hero');
  if (!nav) return;

  let lastScrollY = 0;
  let ticking = false;

  const handleScroll = () => {
    const currentScrollY = window.scrollY || document.documentElement.scrollTop;
    const heroHeight = hero ? hero.offsetHeight : window.innerHeight;

    // Transparent → solid threshold at hero bottom
    if (currentScrollY >= heroHeight - nav.offsetHeight) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }

    // Hide on scroll down, show on scroll up
    if (currentScrollY > lastScrollY && currentScrollY > 300) {
      nav.classList.add('hidden');
    } else {
      nav.classList.remove('hidden');
    }

    lastScrollY = currentScrollY;
    ticking = false;
  };

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(handleScroll);
      ticking = true;
    }
  }, { passive: true });

  handleScroll(); // run once on load
}

/* ───────────────────────────────────────────────────────────────
   ACTIVE NAV LINK HIGHLIGHT
   ─────────────────────────────────────────────────────────────── */
function initActiveNavLinks() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');
  if (!navLinks.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navLinks.forEach(l => l.classList.remove('active'));
        const active = document.querySelector(`.nav-link[href="#${entry.target.id}"]`);
        if (active) active.classList.add('active');
      }
    });
  }, { threshold: 0.4 });

  sections.forEach(s => observer.observe(s));
}

/* ───────────────────────────────────────────────────────────────
   MOBILE DRAWER
   ─────────────────────────────────────────────────────────────── */
function initMobileDrawer() {
  const hamburger = document.getElementById('nav-hamburger');
  const drawer    = document.getElementById('nav-drawer');
  const overlay   = document.getElementById('nav-drawer-overlay');
  const closeBtn  = document.getElementById('nav-drawer-close');
  const drawerLinks = document.querySelectorAll('.nav-drawer-link, .nav-drawer-cta');

  if (!hamburger || !drawer) return;

  const openDrawer = () => {
    drawer.classList.add('open');
    overlay.classList.add('open');
    hamburger.classList.add('open');
    hamburger.setAttribute('aria-expanded', 'true');
    drawer.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  };

  const closeDrawer = () => {
    drawer.classList.remove('open');
    overlay.classList.remove('open');
    hamburger.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
    drawer.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  };

  hamburger.addEventListener('click', openDrawer);
  closeBtn.addEventListener('click', closeDrawer);
  overlay.addEventListener('click', closeDrawer);
  drawerLinks.forEach(link => link.addEventListener('click', closeDrawer));
}



/* ───────────────────────────────────────────────────────────────
   COLLECTIONS ANIMATIONS
   ─────────────────────────────────────────────────────────────── */
function initCollections() {
  const collectionsTitle = document.querySelector('.collections-title');
  const collectionsSubtext = document.querySelector('.collections-subtext');
  const cards = document.querySelectorAll('.collection-card:not(.hidden-card)');
  const viewMoreBtn = document.getElementById('view-more-btn');
  const hiddenCards = document.querySelectorAll('.hidden-card');

  if (collectionsTitle) {
    gsap.from(collectionsTitle, {
      y: 40,
      opacity: 0,
      duration: 1,
      ease: 'power3.out',
      scrollTrigger: {
        trigger: '.collections',
        start: 'top 70%',
        toggleActions: 'play none none reverse',
      },
    });

    gsap.from(collectionsSubtext, {
      y: 20,
      opacity: 0,
      duration: 1,
      delay: 0.2,
      ease: 'power3.out',
      scrollTrigger: {
        trigger: '.collections',
        start: 'top 70%',
        toggleActions: 'play none none reverse',
      },
    });

    if (cards.length > 0) {
      gsap.from(cards, {
        y: 60,
        opacity: 0,
        duration: 1,
        stagger: 0.15,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: '.collections-grid',
          start: 'top 75%',
          toggleActions: 'play none none reverse',
        },
      });
    }
  }

  if (viewMoreBtn) {
    viewMoreBtn.addEventListener('click', () => {
      // Show hidden cards
      hiddenCards.forEach(card => {
        card.style.display = 'block';
        gsap.fromTo(card, 
          { opacity: 0, y: 30 }, 
          { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out' }
        );
      });
      // Hide the view more button
      viewMoreBtn.style.display = 'none';
      ScrollTrigger.refresh();
    });
  }
}

/* ───────────────────────────────────────────────────────────────
   REELS CAROUSEL ANIMATIONS
   ─────────────────────────────────────────────────────────────── */
function initReelsCarousel() {
  const cards = document.querySelectorAll('.reel-card');
  const nextBtn = document.querySelector('.next-btn');
  const prevBtn = document.querySelector('.prev-btn');
  const carousel = document.querySelector('.reels-carousel');
  
  if (!cards.length) return;

  let currentIndex = 0;
  let isMobile = window.innerWidth <= 768;
  let isDropsInView = false;
  const getOffset = () => window.innerWidth <= 768 ? 100 : 350;

  function updateCarousel(animDuration = 0.6) {
    const offset = getOffset();

    cards.forEach((card, i) => {
      // Pause all videos by default
      const video = card.querySelector('.reel-video');
      video.pause();
      card.classList.remove('is-center');
      
      let xPos = 0;
      let scale = 0.85;
      let opacity = 0;
      let zIndex = 1;

      if (i === currentIndex) {
        xPos = 0;
        scale = window.innerWidth <= 768 ? 1.05 : 1.15;
        opacity = 1;
        zIndex = 5;
        card.classList.add('is-center');
        
        // Handle Video Play
        video.muted = card.dataset.muted === "true" ? true : false;
        updateMuteUI(card, video.muted);
        if (isDropsInView) {
          video.play().catch((err) => {
            // If browser blocks unmuted autoplay, fallback to muted so it still plays
            if (!video.muted && err.name === 'NotAllowedError') {
              video.muted = true;
              card.dataset.muted = "true";
              updateMuteUI(card, true);
              video.play().catch(() => {});
            }
          });
        }

      } else if (i === currentIndex - 1 || (currentIndex === 0 && i === cards.length - 1)) {
        // Left
        xPos = -offset;
        scale = 0.85;
        opacity = 0.8;
        zIndex = 3;
      } else if (i === currentIndex + 1 || (currentIndex === cards.length - 1 && i === 0)) {
        // Right
        xPos = offset;
        scale = 0.85;
        opacity = 0.8;
        zIndex = 3;
      } else {
        // Hidden
        // Determine if it should hide on left or right contextually
        let relativeDistance = i - currentIndex;
        if (relativeDistance > cards.length / 2) relativeDistance -= cards.length;
        if (relativeDistance < -cards.length / 2) relativeDistance += cards.length;

        xPos = relativeDistance < 0 ? -offset * 2 : offset * 2;
        scale = 0.6;
        opacity = 0;
        zIndex = 1;
      }

      gsap.to(card, {
        x: xPos,
        scale: scale,
        opacity: opacity,
        zIndex: zIndex,
        duration: animDuration,
        ease: 'power3.out'
      });
    });
  }

  function nextReel() {
    currentIndex = (currentIndex + 1) % cards.length;
    updateCarousel();
  }

  function prevReel() {
    currentIndex = (currentIndex - 1 + cards.length) % cards.length;
    updateCarousel();
  }

  // AutoPlay Video Logic
  cards.forEach((card, idx) => {
    const video = card.querySelector('.reel-video');
    card.dataset.muted = "false";
    
    // When video ends
    video.addEventListener('ended', () => {
      // Always slide to next when video finishes
      if (card.classList.contains('is-center')) {
        nextReel();
      }
    });

    // Mute/Unmute toggle
    const muteBtn = card.querySelector('.mute-btn');
    if (muteBtn) {
      muteBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        video.muted = !video.muted;
        card.dataset.muted = video.muted ? "true" : "false";
        updateMuteUI(card, video.muted);
      });
    }

    // Click on side reels to navigate, center reel to open Instagram
    card.addEventListener('click', (e) => {
      if (!card.classList.contains('is-center') && !e.target.closest('.mute-btn')) {
        let isRight = false;
        if (idx === currentIndex + 1 || (currentIndex === cards.length - 1 && idx === 0)) isRight = true;
        
        if (isRight) nextReel();
        else prevReel();
      } else if (card.classList.contains('is-center') && !e.target.closest('.mute-btn')) {
        const url = card.dataset.url || 'https://instagram.com/inklayer';
        window.open(url, '_blank');
      }
    });
  });

  function updateMuteUI(card, isMuted) {
    const onIcon = card.querySelector('.mute-on');
    const offIcon = card.querySelector('.mute-off');
    if (isMuted) {
      onIcon.style.display = 'block';
      offIcon.style.display = 'none';
    } else {
      onIcon.style.display = 'none';
      offIcon.style.display = 'block';
    }
  }

  // Controls
  if (nextBtn) nextBtn.addEventListener('click', nextReel);
  if (prevBtn) prevBtn.addEventListener('click', prevReel);

  // Swipe logic
  let startX = 0;
  if (carousel) {
    carousel.addEventListener('touchstart', e => {
      startX = e.touches[0].clientX;
    }, {passive: true});

    carousel.addEventListener('touchend', e => {
      const endX = e.changedTouches[0].clientX;
      if (startX - endX > 50) nextReel(); // Swipe left -> slide right
      if (endX - startX > 50) prevReel(); // Swipe right -> slide left
    });
  }

  // Intersection Observer to stop playing when not in view
  const dropsSection = document.getElementById('drops');
  if (dropsSection) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        isDropsInView = entry.isIntersecting;
        if (!isDropsInView) {
          // Pause all videos
          cards.forEach(c => c.querySelector('.reel-video').pause());
        } else {
          // Play the center video
          const centerCard = Array.from(cards).find(c => c.classList.contains('is-center'));
          if (centerCard) {
            const video = centerCard.querySelector('.reel-video');
            video.play().catch((err) => {
              if (!video.muted && err.name === 'NotAllowedError') {
                video.muted = true;
                centerCard.dataset.muted = "true";
                updateMuteUI(centerCard, true);
                video.play().catch(() => {});
              }
            });
          }
        }
      });
    }, { threshold: 0.1 });
    observer.observe(dropsSection);
  }

  // Initialize
  updateCarousel(0);
}

/* ───────────────────────────────────────────────────────────────
   ABOUT INKLAYER ANIMATIONS
   ─────────────────────────────────────────────────────────────── */
function initAboutAnimations() {
  const aboutSection = document.querySelector('.about-inklayer');
  const aboutBg = document.querySelector('.about-bg-img');
  const aboutTextBlock = document.querySelector('.about-text-block');

  if (!aboutSection) return;

  // Background slightly zooms (parallax feel)
  if (aboutBg) {
    gsap.fromTo(aboutBg, 
      { scale: 1 },
      {
        scale: 1.08,
        ease: 'none',
        scrollTrigger: {
          trigger: aboutSection,
          start: 'top bottom',
          end: 'bottom top',
          scrub: true,
        }
      }
    );
  }

  // Fade-in + slight slide from left
  if (aboutTextBlock) {
    gsap.fromTo(aboutTextBlock, 
      { x: -40, opacity: 0 },
      {
        x: 0,
        opacity: 1,
        duration: 1.2,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: aboutSection,
          start: 'top 70%',
          toggleActions: 'play none none reverse',
        }
      }
    );
  }
}

/* ───────────────────────────────────────────────────────────────
   JOIN THE DROP - BACKEND INTEGRATION
   ─────────────────────────────────────────────────────────────── */
function initJoinDropForm() {
  const form = document.getElementById('join-drop-form');
  const emailInput = document.getElementById('join-drop-email');
  const submitBtn = document.getElementById('join-drop-btn');
  const privacyText = document.querySelector('.join-drop-privacy');

  if (!form) return;

  const originalPrivacyText = privacyText.innerText;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = emailInput.value.trim();
    if (!email) return;

    // Loading State
    const originalBtnText = submitBtn.innerText;
    submitBtn.innerText = 'Joining...';
    submitBtn.disabled = true;
    submitBtn.style.opacity = '0.7';
    privacyText.style.color = ''; // reset previous error color

    try {
      const response = await fetch('http://localhost:8000/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      const data = await response.json();

      if (response.ok) {
        const innerContainer = document.querySelector('.join-drop-inner');
        
        if (data.success) {
          innerContainer.innerHTML = `
            <span class="join-drop-eyebrow" style="color: #a3a3a3;">ACCESS GRANTED</span>
            <h2 class="join-drop-title" style="margin-bottom: 0.5rem;">YOU’RE IN</h2>
            <p class="join-drop-subtext" style="color: #ffffff; font-size: 1.25rem;">Drop access unlocked. Check your inbox.</p>
            <p class="join-drop-privacy" style="margin-top: 1.5rem; color: #888;">Email may take a few seconds to arrive</p>
          `;
        } else {
          // Soft error (duplicate)
          innerContainer.innerHTML = `
            <span class="join-drop-eyebrow" style="color: #a3a3a3;">STATUS: ACTIVE</span>
            <h2 class="join-drop-title" style="margin-bottom: 0.5rem;">ALREADY ON LIST</h2>
            <p class="join-drop-subtext" style="color: #ffffff; font-size: 1.25rem;">${data.message}</p>
          `;
        }
        return; // Don't process finally block's DOM resets since form is removed
      } else {
        // Handle validation or rate limit gracefully vs raw errors
        let errorMsg = 'Something went wrong. Please try again.';
        
        if (response.status === 429) {
          errorMsg = 'Too many attempts. Please try again in a minute.';
        } else if (response.status === 422) {
          errorMsg = 'Please enter a valid email address.';
        } else if (data.detail) {
          errorMsg = typeof data.detail === 'string' ? data.detail : errorMsg;
        }

        submitBtn.innerText = 'Try Again';
        privacyText.innerText = errorMsg;
        privacyText.style.color = '#ff5b5b'; // Subtle red
      }
    } catch (err) {
      submitBtn.innerText = 'Server Error';
      privacyText.innerText = 'Network connection failed. Try again later.';
      privacyText.style.color = '#ff5b5b';
    } finally {
      // Only reset the button state if the form still exists in the DOM
      if (document.getElementById('join-drop-form')) {
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.style.opacity = '1';
          submitBtn.innerText = originalBtnText;
          if (privacyText.style.color !== '') {
            setTimeout(() => {
               privacyText.style.color = '';
               privacyText.innerText = originalPrivacyText;
            }, 3000); // Revert error message back to normal after a brief delay
          }
        }, 2500); // Wait before re-enabling entirely
      }
    }
  });
}

/* ───────────────────────────────────────────────────────────────
   INITIALIZE EVERYTHING
   ─────────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initHeroAnimations();
  initNavScroll();
  initActiveNavLinks();
  initMobileDrawer();
  initCollections();
  initReelsCarousel();
  initAboutAnimations();
  initJoinDropForm();
  
  // Initialize Metallic Logo effect
  initMetallicLogo('#nav-logo-link');
});

window.addEventListener('load', () => {
  ScrollTrigger.refresh();
});
