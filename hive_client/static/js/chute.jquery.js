'use strict';
/*
2014. Ross Crawford-d'Heureuse to be a jquery.plugin
*/
$(function() {

    function UninitializedObjectException(message) {
       this.message = message;
       this.name = "UserException";
    }

    $.widget( "hive_client.hive_client_controller", {
        // default options
        timer: undefined,
        wait_for: undefined,
        template: undefined,
        current_feeditem: undefined,

        options: {
            'feed': undefined,
            'project': undefined,
            'templates': undefined,
            'settings': undefined,
            'renderer': Handlebars || undefined,
            'listeners': [],

            'target': $('div#content'),

            'DEBUG': true,                              // -- show debug messages
        },

        log: function (msg) {
            var self = this;
            if (self.options.DEBUG === true) {
                console.log(msg)
            }
        },
        // the constructor
        _create: function() {
            var self = this;

            if ( this.options.feed === undefined ) {
                throw new UninitializedObjectException("You need to initialize the hive_client_controller");
            }
            try {
                self.current_feeditem = this.options.feed[0];
                self.wait_for = self.current_feeditem.wait_for;
                self.template_name = self.current_feeditem.template_name;
            } catch ( err ) {
                self.current_feeditem = {};
                self.wait_for = 3600;
                self.template_name = 'no_content';
            }

            this._listen();
            this._begin();
        },
        _listen: function () {
            var self = this;
            $.each(this.options.listeners, function ( index, listener ) {
                self.log('Listener: ' + index);
                listener(self.current_feeditem, self.options);
            });

        },
        timeout: function () {
            var timeout_in = (this.wait_for * 1000);
            this.log('Timeout set to: ' + timeout_in);
            return timeout_in;
        },
        _timer: function () {
            var self = this;
            if ( self.timer !== undefined ) {
                // the main timer object
                window.clearTimeout( self.timer );
            }
            // ensure we have more than 1 item in the feed for the rotator
            if ( self.options.feed && self.options.feed.length > 1 ) {

                self.timer = window.setTimeout( function () {
                    // when it expires call next
                    $( 'body' ).trigger( 'end_progress', [] );
                    self.next();
                }, self.timeout());
            }
        },
        _begin: function () {
            var self = this;

            // setup window setTime and window.clearTimer handler
            var source = this.options.templates[self.template_name];

            // @TODO move this to a more logical place
            // reload it after every 10? items shown
            $( 'body' ).trigger( 'hive_client.begin' );

            self.render( source );
            self._timer();
        },
        picture_is_local: function ( feed_item ) {
            var self = this;
            var is_present = false;
            if (!feed_item.picture || feed_item.picture === undefined) {
                return {'is_present': false, 'filename': null};
            }

            var pic = feed_item.picture.split('/');
            var pic_filename = pic[pic.length - 1]

            $.ajax({
                type: "HEAD",
                async: false,
                url: '/media/' + pic_filename,
                success: function(message,text,response){
                    is_present = true;
                },
                error: function(message,text,response){
                  is_present = false;
                }
            });
            return {'is_present': is_present, 'filename': pic_filename};
        },
        video_is_local: function ( feed_item ) {
            var self = this;
            var is_present = false;
            if (!feed_item.video || feed_item.video === undefined) {
                return {'is_present': false, 'filename': null};
            }

            var vid = feed_item.video.split('/');
            var vid_filename = vid[vid.length - 1]

            $.ajax({
                type: "HEAD",
                async: false,
                url: '/media/' + vid_filename,
                success: function(message,text,response){
                    is_present = true;
                },
                error: function(message,text,response){
                  is_present = false;
                }
            });

            return {'is_present': is_present, 'filename': vid_filename};
        },
        render: function ( source ) {
            var self = this;
            var target = self.options.target;

            var compiled = self.options.renderer.compile( source );

            var pic_is_present = self.picture_is_local(this.current_feeditem)
            if ( pic_is_present.is_present === true ) {
                this.current_feeditem.picture = '/media/' + pic_is_present.filename;
            }
            var vid_is_present = self.video_is_local(this.current_feeditem)
            if ( vid_is_present.is_present === true ) {
                this.current_feeditem.video = '/media/' + vid_is_present.filename;
            }

            var context = {
                'project': this.options.project,
                'object': this.current_feeditem,
                'settings': this.options.settings,
            };

            var html = compiled( context );
            //this.log(context);
            //this.log(html);
            this.log('starting progress')
            $( 'body' ).trigger( 'start_progress', [ this.wait_for ] );
            target.html( html );
        },
        goto: function ( pk ) {
            var self = this;

            this.log('Loading goto: ' + pk) ;

            $.each(this.options.feed, function ( index, feed_item ) {
                if ( feed_item.pk === pk ) {

                    self.next_item_by_index( index );

                    return false;
                }
            });

        },
        next: function () {
            var self = this;

            this.log('Loading next') ;

            $.each(this.options.feed, function ( index, feed_item ) {

                self.log('Check for current and get next: ' + index +'');
                self.log('Current iteration PKs: feed_item:'+ feed_item.pk +' current_feeditem: '+ self.current_feeditem.pk);

                if ( feed_item.pk === self.current_feeditem.pk ) {
                    var next_pk = parseInt( index + 1 );

                    self.next_item_by_index( next_pk );

                    return false;
                }
            });
        },
        next_item_by_index: function ( index ) {
            var self = this;
            var next_item = null;

            try {
               next_item = self.options.feed[ index ];
               self.log('i+1: '+ index)
               self.log('next_item set to: ' + next_item.pk);
            }
            catch (e) {
               // error occurred assume index error for now and set to 0
               // for loop
               next_item = self.options.feed[0];
               self.log('Error: next_item set to index 0: ' + next_item + ' error: ' + e.message);
            }

            var self = this;
            self.current_feeditem = next_item;

            self.template_name = next_item.template_name;
            self.log('Template set to: ' + next_item.template_name);

            self.wait_for = next_item.wait_for;
            self.log('Wait_for set to: ' + next_item.wait_for);

            self.render( self.options.templates[self.template_name] );
            self._timer();
        }
    });
});