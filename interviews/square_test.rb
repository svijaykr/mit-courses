require 'rspec'
require './square'

describe Client do
  it 'gets the correct treasure' do
    treasure = [[235,450], [150, 200]]
    server = Server.new(500, treasure)
    client = Client.new(server)

    expect(client.search).to eq([150, 200])
  end
end

describe BloomFilter do
  it 'remembers an element' do
    filter = BloomFilter.new(100, 3)
    filter.add([5,5])

    expect(filter.test([5,5])).to eq(true)
  end

  it 'probably doesnt give false positives' do
    filter = BloomFilter.new(100, 3)
    filter.add([5,5])

    expect(filter.test([6,1])).to eq(false)
  end
end
