require 'digest/sha1'

class Server
  attr_reader :size

  def initialize(size, treasures)
    @size = size
    @treasures = treasures
  end

  def answer_filter
    filter = BloomFilter.new(128, 3)
    @treasures.each do |tuple|
      filter.add(tuple)
    end

    filter
  end

  def test(tuple)
    puts "testing #{tuple}"
    @treasures.include?(tuple)
  end
end

class Client
  def initialize(server)
    @server = server
  end

  def search
    answer_filter = @server.answer_filter
    0.upto(@server.size).each do |i|
      0.upto(@server.size).each do |j|
        if answer_filter.test([i,j])
          return [i,j] if @server.test([i,j])
        end
      end
    end
  end
end

class Hasher
  class << self
    def hash(tuple)
      Digest::SHA1.hexdigest(tuple.join(""))
    end
  end
end

class BloomFilter
  attr_reader :size, :k

  def initialize(size, k)
    @size = size
    @k = k
    @filter = [0]*size
  end

  def add(element)
    get_hashes(element).each do |i|
      @filter[i] = 1
    end
  end

  def test(element)
    get_hashes(element).each do |i|
      return false if @filter[i] == 0
    end
    return true
  end

  private

    def get_hashes(element)
      ints = 0.upto(k).collect do |i|
        Hasher.hash(element).slice(i*5, (i+1)*5).to_i(16)
      end

      ints.collect do |i|
        i % @size
      end
    end
end
