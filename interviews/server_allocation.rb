require 'minitest/autorun'

class ServerAllocator
  def initialize()
    @current_servers = Hash.new { |hash, key| hash[key] = {} }
  end

  # Returns a server of type +Server+
  def allocate_server(type)
    server_id = next_available_server_id(type)
    server_hash(type)[server_id] = Server.new(type, server_id)
  end

  def deallocate_server(server_id)
    server_hash(type).delete(server_id)
  end

  def is_allocated?(type, server_id)
    server_hash(type)[server_id]
  end

  private

    def server_hash(type)
      @current_servers[type]
    end

    def next_available_server_id(type)
      smallest_integer(server_hash(type).collect { |k,v| k })
    end

    def smallest_integer(integers)
      integers = integers.uniq.sort
      integers.each_with_index do |integer, index|
        return index+1 if integers[index] != index + 1
      end

      integers.size + 1
    end
end

class Server
  attr_reader :server_type, :server_id

  def initialize(server_type, server_id)
    @server_type = server_type
    @server_id = server_id
  end
end

class ServerAllocationTests < Minitest::Test
  def setup
    @allocator = ServerAllocator.new
  end

  def test_allocation_start
    @allocator.allocate_server('some_type')
    assert @allocator.is_allocated?('some_type', 1)
  end

  def test_different_type_allocation
    @allocator.allocate_server('t1')
    @allocator.allocate_server('t2')
    assert @allocator.is_allocated?('t1', 1)
    assert @allocator.is_allocated?('t2', 1)
  end

  def test_allocate_multiple
    @allocator.allocate_server('t1')
    @allocator.allocate_server('t1')
    @allocator.allocate_server('t1')
    assert @allocator.is_allocated?('t1', 1)
    assert @allocator.is_allocated?('t1', 2)
    assert @allocator.is_allocated?('t1', 3)
  end
end
