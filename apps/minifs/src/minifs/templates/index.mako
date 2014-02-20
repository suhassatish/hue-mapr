<%!from desktop.views import commonheader, commonfooter %>
<%namespace name="shared" file="shared_components.mako" />

${commonheader("Minifs", "minifs", user) | n,unicode}
${shared.menubar(section='mytab')}

## Use double hashes for a mako template comment
## Main body

<%! from filebrowser.views import location_to_url %>

<div class="container-fluid">
  <div class="card">
    <h2 class="card-heading simple">Minifs app is successfully setup!</h2>
    <div class="card-body">
      <p>It's now ${date}.</p>
    </div>

  <div style="padding-left:15px">
    % for file in files:
      <div class="row">        
        <span class="span6"><a href="${ location_to_url(file['path'], False) }">${ file['path'] }</a></span>        
        <span class="span6">${ file['user'] }</span>        
      </div>
    % endfor
  </div>
    
  </div>
</div>
${commonfooter(messages) | n,unicode}
