echo -n "Source: "
echo `wc -l \`find -iwholename "./src/*.py"\` | grep total`
echo -n "Test:   "
echo `wc -l \`find -iwholename "./tests/*.py"\` | grep total`
