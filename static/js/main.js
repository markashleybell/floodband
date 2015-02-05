var FloodSite = (function($, window, moment) {
    var _sound = null;
    var _soundcloudid = null;
    var _trackLinkClick = function(category, action, label, callback) {
        ga('send', {
            'hitType': 'event',
            'eventCategory': category,
            'eventAction': action,
            'eventLabel': label,
            'hitCallback': callback
        });
    };
    var _activateUrls = function(text) {
        return text.replace(/\s(https?:\/\/[^\s\<]+)(\s)?/gi, ' <a href="$1">$1</a>$2');
    };
    var _init = function() {
        $.ajax({
            url: '/statuses',
            data: {},
            dataType: 'json',
            type: 'GET',
            success: function(data, status, request) {
                var output = [];
                $.each(data.statuses, function(i, item) {
                    output.push('<p><span>' + moment(item.created_at).fromNow() + '</span>' + _activateUrls(item.text) + '</p>');
                });
                $('#tweet-container').html(output.join('') + '<p><a class="social" title="Twitter" href="https://twitter.com/floodbanduk">Follow Flood on Twitter</a></p>');
            },
            error: function(request, status, error) { console.log(error); }
        });
        $('a.social').on('click', function(e) {
            e.preventDefault();
            var link = $(this);
            _trackLinkClick('External Link', 'Click', link.attr('title'), function() {
                window.location = link.attr('href');
            });
        });
        var controls = $('ul.tracklisting a span');
        var loaders = $('ul.tracklisting img.loader');
        $('ul.tracklisting a').on('click', function(e) {
            e.preventDefault();
            var link = $(this);
            var soundcloudid = link.data('soundcloudid');
            var title = link.attr('title');
            var icon = link.find('span');
            var loader = link.next('img.loader');
            // If a sound is currently playing
            if(_sound !== null) {
                // If the currently playing song is the same one 
                // that was just clicked, toggle pause state
                if(_soundcloudid === soundcloudid) {
                    if(!_sound.paused) {
                        icon.removeClass().addClass('icon-play');
                        _sound.pause();
                    } else {
                        icon.removeClass().addClass('icon-pause');
                        _sound.play();
                    }
                } else {
                    _sound.destruct();
                    controls.removeClass().addClass('icon-play');
                    loader.css('display', 'inline');
                    _trackLinkClick('Song Play', 'Click', title, function() {
                        SC.stream('/tracks/' + soundcloudid, function(sound) {
                            _soundcloudid = soundcloudid;
                            _sound = sound;
                            icon.removeClass().addClass('icon-pause');
                            loader.hide();
                            _sound.play();
                        });
                    });
                }
            } else {
                loader.css('display', 'inline');
                _trackLinkClick('Song Play', 'Click', title, function() {
                    SC.stream('/tracks/' + soundcloudid, function(sound) {
                        _soundcloudid = soundcloudid;
                        _sound = sound;
                        icon.removeClass().addClass('icon-pause');
                        loader.hide();
                        _sound.play();
                    });
                });
            }
        });
        $('#mailing-list-subscribe').on('submit', function(e) {
            var form = $(this);
            e.preventDefault();
            $.ajax({
                url: form.attr('action'),
                data: form.serialize(),
                type: 'POST'
            }).done(function(data, status, req) {
                form.replaceWith('<p><strong>Thanks! You\'re all signed up. You can remove yourself from our list by clicking on the \'unsubscribe\' link at the bottom of any of our emails.</strong></p>');
            }).fail(function(req, status, error) {
                form.find('.error').remove();
                form.append('<p class="error"><strong>Sorry, there was a problem signing you up! Please check you typed your email address correctly.</strong></p>');
            });
        });
    };
    return {
        init: _init
    };
}(jQuery, window, moment));