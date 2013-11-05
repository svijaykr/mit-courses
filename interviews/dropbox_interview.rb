class HitCounter

  # Class for counting the number of hits.
  # Arguments:
  #   time_interval : time window to get sum of hits from (seconds)
  #   cache_clear_interval : time after which cache is cleared in a hit (seconds)
  def initialize(time_interval, cache_clear_interval)
    @hits_count = Hash.new { |hash, val| hash[val] = 0 }
    @time_interval = time_interval
    @cache_clear_interval = cache_clear_interval
    @last_cache_clear = nil
  end

  def add_hit
    time = Time.now
    closest_second = time / 1000
    @hits_count[closest_second] += 1
    clear_cache(time)
  end

  def get_hits
    current_time = Time.now
    seconds_minutes_ago(current_time).upto(current_time / 1000).collect { |i| @hits_count[i] }.sum
  end

  private

    def seconds_minutes_ago(time)
      (time / 1000) - @time_interval
    end

    def clear_cache(time)
      return if @last_cache_clear && time - @last_cache_clear < @cache_clear_interval * 1000

      end_clear = seconds_minutes_ago(time)
      @hits_count.each do |key, value|
        @hits_count.delete(key) if key < end_clear
      end
    end
end
