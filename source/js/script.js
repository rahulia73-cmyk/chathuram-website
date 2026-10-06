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
			'Hello Chathuram Chess Academy, I would like to book a free trial class.',
			'',
			'Name: ' + get('name'),
			'Phone: ' + get('phone'),
			'City: ' + get('city'),
			'Student age: ' + get('age'),
			'Level: ' + get('program'),
			'Class type: ' + get('mode')
		];
		if (get('message')) {
			lines.push('', get('message'));
		}
		window.open('https://wa.me/' + number + '?text=' + encodeURIComponent(lines.join('\n')), '_blank', 'noopener');
	});

})(jQuery);

// Pawn path: the mascot spin-jumps up one slanted square per level,
// from 01 Beginner to 08 Grand Master. On the last square it promotes,
// spinning into a queen, knight, rook and bishop: every pawn can become more.
(function () {
	'use strict';

	var root = document.querySelector('[data-pawn-path]');
	if (!root || !root.animate) {
		return;
	}

	var tiles = Array.prototype.slice.call(root.querySelectorAll('.pp-tile'));
	var pawn = root.querySelector('.pp-pawn');
	var spin = root.querySelector('.pp-spin');
	var glow = root.querySelector('.pp-glow');
	var toggle = root.querySelector('.pawn-path-toggle');
	var captionLevel = root.querySelector('.pp-caption-level');
	var captionName = root.querySelector('.pp-caption-name');
	var last = tiles.length - 1;
	var promotions = ['queen', 'knight', 'rook', 'bishop'];
	var names = { pawn: 'Pawn', queen: 'Queen', knight: 'Knight', rook: 'Rook', bishop: 'Bishop' };
	var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	// spin around the middle of the piece, not its feet
	var PIVOT = 72;

	var pos = function (i) {
		return { x: parseFloat(tiles[i].getAttribute('data-x')), y: parseFloat(tiles[i].getAttribute('data-y')) };
	};
	var at = function (x, y) {
		return 'translate(' + x + 'px, ' + y + 'px)';
	};
	var turn = function (deg, sx, sy) {
		return 'translate(0px, -' + PIVOT + 'px) rotate(' + deg + 'deg) translate(0px, ' + PIVOT + 'px) scale(' + sx + ', ' + sy + ')';
	};
	var caption = function (level, name) {
		if (captionLevel) {
			captionLevel.textContent = level;
			captionName.textContent = name;
		}
	};
	var place = function (i) {
		var p = pos(i);
		pawn.style.transform = at(p.x, p.y);
		caption('Level ' + tiles[i].getAttribute('data-level'), tiles[i].getAttribute('data-name'));
	};
	var become = function (piece) {
		Array.prototype.forEach.call(root.querySelectorAll('.pp-piece'), function (g) {
			g.classList.toggle('is-current', g.getAttribute('data-piece') === piece);
		});
	};
	var clear = function () {
		tiles.forEach(function (t) {
			t.classList.remove('is-target', 'is-visited');
		});
	};
	var sparkle = function () {
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
	var busy = false;
	var hops = 0;

	var wait = function (ms, fn) {
		if (playing) {
			timer = window.setTimeout(fn, ms);
		}
	};

	// one jump: the body travels along an arc while the piece spins and squashes
	var jump = function (from, to, opts, done) {
		var a = pos(from);
		var b = pos(to);
		var dir = hops++ % 2 ? -1 : 1;
		var turns = 360 * (opts.turns || 1) * dir;
		var duration = opts.duration || 760;
		busy = true;
		pawn.animate([
			{ transform: at(a.x, a.y) },
			{ transform: at(a.x, a.y), offset: 0.12 },
			{ transform: at((a.x + b.x) / 2, (a.y + b.y) / 2 - opts.lift), offset: 0.52, easing: 'ease-in' },
			{ transform: at(b.x, b.y), offset: 0.88 },
			{ transform: at(b.x, b.y) }
		], { duration: duration, easing: 'ease-out' });
		var anim = spin.animate([
			{ transform: turn(0, 1, 1) },
			{ transform: turn(0, 1.18, 0.78), offset: 0.12 },
			{ transform: turn(0, 0.9, 1.12), offset: 0.2 },
			{ transform: turn(turns, 1, 1), offset: 0.8 },
			{ transform: turn(turns, 1.16, 0.8), offset: 0.9 },
			{ transform: turn(turns, 1, 1) }
		], { duration: duration, easing: 'ease-in-out' });
		if (opts.swapTo) {
			window.setTimeout(function () {
				become(opts.swapTo);
				if (opts.onSwap) {
					opts.onSwap();
				}
			}, duration * 0.5);
		}
		anim.onfinish = function () {
			busy = false;
			spin.style.transform = '';
			done();
		};
	};

	var step;

	var promote = function (k) {
		if (!playing) {
			return;
		}
		if (k === promotions.length) {
			wait(1400, function () {
				pawn.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 300, fill: 'forwards' }).onfinish = function () {
					clear();
					become('pawn');
					current = 0;
					place(0);
					pawn.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 300, fill: 'forwards' });
					wait(700, step);
				};
			});
			return;
		}
		var piece = promotions[k];
		jump(last, last, { lift: 70, turns: 2, duration: 1000, swapTo: piece }, function () {
			sparkle();
			caption('Promotion', 'Pawn → ' + names[piece]);
			wait(1100, function () {
				promote(k + 1);
			});
		});
	};

	step = function () {
		if (!playing) {
			return;
		}
		if (current === last) {
			promote(0);
			return;
		}
		var next = current + 1;
		tiles[next].classList.add('is-target');
		wait(300, function () {
			jump(current, next, { lift: 60 }, function () {
				for (var i = 0; i < next; i++) {
					tiles[i].classList.add('is-visited');
				}
				tiles[next].classList.remove('is-target');
				current = next;
				place(current);
				wait(current === last ? 400 : 380, step);
			});
		});
	};

	var start = function () {
		if (playing || paused || !visible || document.hidden) {
			return;
		}
		playing = true;
		// a jump already in flight carries on into the next step by itself
		if (!busy) {
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
