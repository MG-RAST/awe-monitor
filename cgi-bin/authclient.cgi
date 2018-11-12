#!/usr/bin/perl

# This is an example of a client handler for oAuth2 authentication servers
# compatible with authServer. It needs to be located on the webserver of your application.
# Use AuthConfig.pm for configuration.
#
# This script will write a cookie COOKIE_NAME with the user information, then redirect
# to the APPLICATION_URL.
# To use it, check for the cookie and redirect to this script if it is not present. If it
# is present, it can be JSON parse to an object with the following keys:
#    name  - full name of the user
#    login - login of the user
#    email - email address of the user
#    admin - boolean whether the user is an admin
#    token - the access token to be used for authentication against the authServer

use strict;
use warnings;

use CGI;
use CGI::Cookie;
use JSON;
use LWP::UserAgent;
use URI::Escape;


use AuthConfig \%ENV;


#print STDERR "2) authclient.cgi SELF_URL: ".$ENV{'SELF_URL'}."\n";
#print STDERR "3) authclient.cgi APPLICATION_NAME: ".AuthConfig::APPLICATION_NAME."\n";


my $json = new JSON;
my $cgi = new CGI();

my $settings = { app_id => AuthConfig::APPLICATION_NAME,
		 app_secret => AuthConfig::APPLICATION_SECRET,
		 dialog_url => AuthConfig::AUTH_URL.'/oAuth.cgi?action=dialog',
		 token_url  => AuthConfig::AUTH_URL.'/oAuth.cgi?action=token',
		 data_url   => AuthConfig::AUTH_URL.'/oAuth.cgi?action=data'
		 };

my $app_id = $settings->{app_id};
my $app_secret = $settings->{app_secret};
my $dialog_url = $settings->{dialog_url};
my $token_url = $settings->{token_url};
my $data_url = $settings->{data_url};

my $my_url = AuthConfig::APPLICATION_URL ; 
$my_url =~ s/\/+$//;
$my_url .= "/cgi-bin/authclient.cgi";


my $code = $cgi->param('code');

unless (defined($code)) {
    my $call_url = $dialog_url."&client_id=" . $app_id . "&redirect_url=" . uri_escape($my_url);
    print $cgi->redirect( -uri => $call_url );
    exit 0;
}

my $call_url = $token_url . "&client_id=" . $app_id . "&client_secret=" . $app_secret . "&code=" . $code;
my $ua = LWP::UserAgent->new;
my $response = $json->decode($ua->get($call_url)->content);
my $access_token = $response->{token};
$call_url = $data_url . "&access_token=" . $access_token;
$response = $ua->get($call_url)->content;
my $cookie = CGI::Cookie->new( -name    => AuthConfig::COOKIE_NAME,
			       -value   => $response,
			       -expires => AuthConfig::COOKIE_EXPIRATION );

print $cgi->redirect(-uri => AuthConfig::APPLICATION_URL, -cookie => $cookie);

exit 0;
