#!/usr/bin/env ruby
# frozen_string_literal: true

def to_anchor(heading)
	heading = heading.downcase.gsub(/[()]/, "").tr(" ", "-")
	"#" + heading
end

while (line = gets&.chomp)
	next if line !~ /\A#/

	line_matcher = line.match(/\A(#+) (.+)/)
	if !line_matcher
		warn "#{line} starts with a hash but doesn't look like a header"
		next
	end

	hashes, heading = line_matcher.captures
	indent_level = hashes.length - 1
	next if indent_level == 0

	indent = "   " * (indent_level - 1)
	puts "#{indent}1. [#{heading}](#{to_anchor(heading)})"
end
