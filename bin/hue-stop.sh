beeswax_pid=`lsof | grep beeswax | awk '{print $2}' | uniq`
`kill $beeswax_pid`

hue_webserver_pid=`lsof | grep runspawning | grep -P "^hue" | awk '{print $2}'`
`kill $hue_webserver_pid`
