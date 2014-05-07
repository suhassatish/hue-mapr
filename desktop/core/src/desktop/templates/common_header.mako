## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
from desktop import conf
import urllib
from desktop.lib.i18n import smart_unicode
from django.utils.translation import ugettext as _
%>

<%def name="is_selected(selected)">
  %if selected:
    class="active"
  %endif
</%def>

<%def name="get_nice_name(app, section)">
  % if app and section == app.display_name:
    - ${app.nice_name}
  % endif
</%def>

<%def name="get_title(title)">
  % if title:
    - ${smart_unicode(title)}
  % endif
</%def>

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Hue ${get_nice_name(current_app, section)} ${get_title(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="">
  <meta name="author" content="">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">

  <link href="/static/ext/css/bootplus.css" rel="stylesheet">
  <link href="/static/ext/css/font-awesome.min.css" rel="stylesheet">
  <link href="/static/css/hue3.css" rel="stylesheet">
  <link href="/static/ext/css/fileuploader.css" rel="stylesheet">

  <style type="text/css">
    % if conf.CUSTOM.BANNER_TOP_HTML.get():
      body {
        padding-top: ${str(int(padding[:-2]) + 40) + 'px'};
        display: none;
      }
      .banner {
        height: 40px;
        width: 100%;
        padding: 0;
        position: fixed;
        top: 0;
        background-color: #F9F9F9;
        z-index: 1033;
      }
      .navigator {
        top: 30px!important;
      }
      .navbar-fixed-top {
        top: 58px!important;
      }
    % else:
      body {
        display: none;
        padding-top: ${padding};
      }
    % endif
  </style>

  <script type="text/javascript" charset="utf-8">

    // jHue plugins global configuration
    jHueFileChooserGlobals = {
      labels: {
        BACK: "${_('Back')}",
        SELECT_FOLDER: "${_('Select this folder')}",
        CREATE_FOLDER: "${_('Create folder')}",
        FOLDER_NAME: "${_('Folder name')}",
        CANCEL: "${_('Cancel')}",
        FILE_NOT_FOUND: "${_('The file has not been found')}",
        UPLOAD_FILE: "${_('Upload a file')}",
        FAILED: "${_('Failed')}"
      },
      user: "${ user.username }"
    };

    jHueTableExtenderGlobals = {
      labels: {
        GO_TO_COLUMN: "${_('Go to column:')}",
        PLACEHOLDER: "${_('column name...')}"
      }
    };

    jHueTourGlobals = {
      labels: {
        AVAILABLE_TOURS: "${_('Available tours')}",
        NO_AVAILABLE_TOURS: "${_('None for this page.')}"
      }
    };

    jHueTourGlobals = {
      labels: {
        AVAILABLE_TOURS: "${_('Available tours')}",
        NO_AVAILABLE_TOURS: "${_('None for this page.')}",
        MORE_INFO: "${_('Read more about it...')}",
        TOOLTIP_TITLE: "${_('Demo tutorials')}"
      }
    };

  </script>

  <!--[if lt IE 9]>
  <script type="text/javascript">
    location.href = "${ url('desktop.views.unsupported') }";
  </script>
  <![endif]-->

  <script type="text/javascript">
    // check if it's a Firefox < 7
    var _UA = navigator.userAgent.toLowerCase();
    for (var i = 1; i < 7; i++) {
      if (_UA.indexOf("firefox/" + i + ".") > -1) {
        location.href = "${ url('desktop.views.unsupported') }";
      }
    }
  </script>

  <script src="/static/js/hue.utils.js"></script>
  <script src="/static/ext/js/jquery/jquery-2.0.2.min.js"></script>
  <script src="/static/js/Source/jHue/jquery.migration.js"></script>
  <script src="/static/js/Source/jHue/jquery.filechooser.js"></script>
  <script src="/static/js/Source/jHue/jquery.selector.js"></script>
  <script src="/static/js/Source/jHue/jquery.alert.js"></script>
  <script src="/static/js/Source/jHue/jquery.rowselector.js"></script>
  <script src="/static/js/Source/jHue/jquery.notify.js"></script>
  <script src="/static/js/Source/jHue/jquery.tablescroller.js"></script>
  <script src="/static/js/Source/jHue/jquery.tableextender.js"></script>
  <script src="/static/js/Source/jHue/jquery.scrollup.js"></script>
  <script src="/static/js/Source/jHue/jquery.tour.js"></script>
  <script src="/static/ext/js/jquery/plugins/jquery.cookie.js"></script>
  <script src="/static/ext/js/jquery/plugins/jquery.total-storage.min.js"></script>
  <script src="/static/ext/js/jquery/plugins/jquery.placeholder.min.js"></script>
  <script src="/static/ext/js/jquery/plugins/jquery.dataTables.1.8.2.min.js"></script>
  <script src="/static/js/jquery.datatables.sorting.js"></script>
  <script src="/static/ext/js/bootstrap.min.js"></script>
  <script src="/static/ext/js/fileuploader.js"></script>
  <script src="/static/js/popover-extra-placements.js"></script>

  <script type="text/javascript" charset="utf-8">
    $(document).ready(function() {
      // prevents framebusting and clickjacking
      if (self == top){
        $("body").show();
      }
      else {
        top.location = self.location;
      }

      $("input, textarea").placeholder();
      $(".submitter").keydown(function (e) {
        if (e.keyCode == 13) {
          $(this).closest("form").submit();
        }
      }).change(function () {
          $(this).closest("form").submit();
      });

      $(".navbar .nav-tooltip").tooltip({
        delay: 0,
        placement: "bottom"
      });

      $("[rel='tooltip']").tooltip({
        delay: 0,
        placement: "bottom"
      });

      $("[rel='navigator-tooltip']").tooltip({
        delay: 0,
        placement: "bottom"
      });

      % if 'jobbrowser' in apps:
      var JB_CHECK_INTERVAL_IN_MILLIS = 30000;
      window.setTimeout(checkJobBrowserStatus, 10);

      function checkJobBrowserStatus(){
        $.getJSON("/${apps['jobbrowser'].display_name}/?format=json&state=running&user=${user.username}", function(data){
          if (data != null){
            if (data.length > 0){
              $("#jobBrowserCount").removeClass("hide").text(data.length);
            }
            else {
              $("#jobBrowserCount").addClass("hide");
            }
          }
          window.setTimeout(checkJobBrowserStatus, JB_CHECK_INTERVAL_IN_MILLIS);
        }).fail(function () {
          window.clearTimeout(checkJobBrowserStatus);
        });
      }
      % endif

      function openDropdown(which, timeout){
        var _this = which;
        var _timeout = timeout!=null?timeout:800;
        if ($(".navigator").find("ul.dropdown-menu:visible").length > 0) {
          _timeout = 10;
        }
        window.clearTimeout(closeTimeout);
        openTimeout = window.setTimeout(function () {
          $(".navigator li.open").removeClass("open");
          $(".navigator ul.dropdown-menu").hide();
          $("[rel='navigator-tooltip']").tooltip("hide");
          _this.find("ul.dropdown-menu").show();
        }, _timeout);
      }

      var openTimeout, closeTimeout;
      $(".navigator ul.nav li.dropdown").on("click", function(){
        openDropdown($(this), 10);
      });
      $(".navigator ul.nav li.dropdown").hover(function () {
        openDropdown($(this));
      },
      function () {
        var _this = $(this);
        window.clearTimeout(openTimeout);
        closeTimeout = window.setTimeout(function () {
          $(".navigator li.open").removeClass("open");
          $(".navigator li a:focus").blur();
          $(".navigator").find("ul.dropdown-menu").hide();
        }, 1000);
      });

      var _skew = -1;
      $("[data-hover]").on("mouseover", function(){
        var _this = $(this);
        _skew = window.setTimeout(function(){
          _this.attr("src", _this.data("hover"));
        }, 3000);
      });

      $("[data-hover]").on("mouseout", function(){
        $(this).attr("src", $(this).data("orig"));
        window.clearTimeout(_skew);
      });
    });
  </script>
</head>
<body>

<div class="navbar navbar-fixed-top">
    % if conf.CUSTOM.BANNER_TOP_HTML.get():
    <div id="banner-top" class="banner">
        ${conf.CUSTOM.BANNER_TOP_HTML.get() | n,unicode }
    </div>
    % endif
    <div class="navbar-inner">
      <div class="container-fluid">
        <a class="brand nav-tooltip" title="${_('About Hue')}" href="/about"><img src="/static/art/hue-logo-mini-letterpress.png" /></a>
        % if user.is_authenticated():
        <div id="usernameDropdown" class="btn-group pull-right">
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
            <i class="icon-user"></i> ${user.username}
            <span class="caret"></span>
          </a>
          <ul class="dropdown-menu">
            <li><a class="userProfile" href="${ url('useradmin.views.edit_user', username=urllib.quote(user.username)) }">${_('Profile')}</a></li>
            <li class="divider"></li>
            <li><a href="/accounts/logout/">${_('Sign Out')}</a></li>
          </ul>
        </div>
        % endif

</div>

% if is_demo:
  <ul class="side-labels unstyled">
    <li class="feedback"><a href="javascript:showClassicWidget()"><i class="fa fa-envelope-o"></i> ${_('Feedback')}</a></li>
  </ul>

  <!-- UserVoice JavaScript SDK -->
  <script>(function(){var uv=document.createElement('script');uv.type='text/javascript';uv.async=true;uv.src='//widget.uservoice.com/8YpsDfIl1Y2sNdONoLXhrg.js';var s=document.getElementsByTagName('script')[0];s.parentNode.insertBefore(uv,s)})()</script>
  <script>
  UserVoice = window.UserVoice || [];
  function showClassicWidget() {
    UserVoice.push(['showLightbox', 'classic_widget', {
      mode: 'feedback',
      primary_color: '#338cb8',
      link_color: '#338cb8',
      forum_id: 247008
    }]);
  }
  </script>
% endif

<div id="jHueNotify" class="alert hide">
    <button class="close">&times;</button>
    <span class="message"></span>
</div>

