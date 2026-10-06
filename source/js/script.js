(function ($) {
	'use strict';

	// Sticky Menu
	$(window).scroll(function () {
		var height = $('.top-header').innerHeight();
		if ($('header').offset().top > 10) {
			$('.top-header').addClass('hide');
			$('.navigation').addClass('nav-bg');
			$('.navigation').css('margin-top', '-' + height + 'px');
		} else {
			$('.top-header').removeClass('hide');
			$('.navigation').removeClass('nav-bg');
			$('.navigation').css('margin-top', '-' + 0 + 'px');
		}
	});

	// Current year in footer
	$('[data-year]').text(new Date().getFullYear());

	// Contact form: no server on GitHub Pages, so send the details as a WhatsApp message
	$('[data-whatsapp-form]').on('submit', function (e) {
		e.preventDefault();
		var form = this;
		var number = String($(form).data('whatsapp-form'));
		var get = function (name) {
			var field = form.elements[name];
			return field ? $.trim(field.value) : '';
		};
		var lines = [
			'Hello Chathuram Chess Academy, I would like to know more about your classes.',
			'',
			'Name: ' + get('name'),
			'Phone: ' + get('phone'),
			'City: ' + get('city'),
			'Student age: ' + get('age'),
			'Level: ' + get('program'),
			'Mode: ' + get('mode')
		];
		if (get('message')) {
			lines.push('', get('message'));
		}
		window.open('https://wa.me/' + number + '?text=' + encodeURIComponent(lines.join('\n')), '_blank', 'noopener');
	});

})(jQuery);

// Pawn path: the mascot climbs one slanted square per level,
// from 01 Beginner to 08 Grand Master.
(function () {
	'use strict';

	var root = document.querySelector('[data-pawn-path]');
	if (!root || !root.animate) {
		return;
	}

	var tiles = Array.prototype.slice.call(root.querySelectorAll('.pp-tile'));
	var pawn = root.querySelector('.pp-pawn');
	var glow = root.querySelector('.pp-glow');
	var toggle = root.querySelector('.pawn-path-toggle');
	var captionLevel = root.querySelector('.pp-caption-level');
	var captionName = root.querySelector('.pp-caption-name');
	var last = tiles.length - 1;
	var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

	var pos = function (i) {
		return { x: parseFloat(tiles[i].getAttribute('data-x')), y: parseFloat(tiles[i].getAttribute('data-y')) };
	};
	var place = function (i) {
		var p = pos(i);
		pawn.style.transform = 'translate(' + p.x + 'px, ' + p.y + 'px)';
		if (captionLevel) {
			captionLevel.textContent = 'Level ' + tiles[i].getAttribute('data-level');
			captionName.textContent = tiles[i].getAttribute('data-name');
		}
	};
	var clear = function () {
		tiles.forEach(function (t) {
			t.classList.remove('is-target', 'is-visited');
		});
		root.classList.remove('is-promoted');
	};
	var promote = function () {
		var p = pos(last);
		glow.setAttribute('cx', p.x);
		glow.setAttribute('cy', p.y);
		root.classList.remove('is-promoted');
		// restart the CSS animation
		glow.getBoundingClientRect();
		root.classList.add('is-promoted');
	};

	if (reduceMotion) {
		place(last);
		tiles[last].classList.add('is-target');
		return;
	}

	var current = 0;
	var timer = null;
	var playing = false;
	var paused = false;
	var visible = true;
	var hopping = false;

	var wait = function (ms, fn) {
		if (playing) {
			timer = window.setTimeout(fn, ms);
		}
	};

	var hop = function (from, to, done) {
		var a = pos(from);
		var b = pos(to);
		var lift = 46 + 20 * (to - from);
		var anim = pawn.animate([
			{ transform: 'translate(' + a.x + 'px, ' + a.y + 'px)' },
			{ transform: 'translate(' + (a.x + b.x) / 2 + 'px, ' + ((a.y + b.y) / 2 - lift) + 'px)', offset: 0.5 },
			{ transform: 'translate(' + b.x + 'px, ' + b.y + 'px)' }
		], { duration: 520 + 140 * (to - from), easing: 'cubic-bezier(.45,0,.3,1)' });
		hopping = true;
		anim.onfinish = function () {
			hopping = false;
			place(to);
			done();
		};
	};

	var step = function () {
		if (!playing) {
			return;
		}
		if (current === last) {
			promote();
			wait(2600, function () {
				clear();
				current = 0;
				place(0);
				wait(700, step);
			});
			return;
		}
		var next = current + 1;
		tiles[next].classList.add('is-target');
		wait(350, function () {
			hop(current, next, function () {
				for (var i = 0; i < next; i++) {
					tiles[i].classList.add('is-visited');
				}
				tiles[next].classList.remove('is-target');
				current = next;
				wait(current === last ? 200 : 550, step);
			});
		});
	};

	var start = function () {
		if (playing || paused || !visible || document.hidden) {
			return;
		}
		playing = true;
		// a hop already in flight carries on into the next step by itself
		if (!hopping) {
			step();
		}
	};
	var stop = function () {
		playing = false;
		window.clearTimeout(timer);
	};

	place(0);

	if ('IntersectionObserver' in window) {
		new IntersectionObserver(function (entries) {
			visible = entries[0].isIntersecting;
			if (visible) {
				start();
			} else {
				stop();
			}
		}).observe(root);
	}
	document.addEventListener('visibilitychange', function () {
		if (document.hidden) {
			stop();
		} else {
			start();
		}
	});

	if (toggle) {
		toggle.hidden = false;
		toggle.addEventListener('click', function () {
			paused = !paused;
			toggle.setAttribute('aria-pressed', String(paused));
			toggle.querySelector('.sr-only').textContent = paused ? 'Play animation' : 'Pause animation';
			toggle.querySelector('i').className = paused ? 'ti-control-play' : 'ti-control-pause';
			if (paused) {
				stop();
			} else {
				start();
			}
		});
	}

	start();
})();
